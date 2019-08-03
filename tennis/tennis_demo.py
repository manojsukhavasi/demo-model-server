import pickle, sys, os, glob, numpy as np, pandas as pd, time, pickle, logging, argparse
import more_itertools as mit
from datetime import datetime

from utils.annotator import Annotator
from utils.utils import *
from utils.pose_utils import *

def current_time():
    return datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

#logging.warning('This will get logged to a file')
#logging.debug('This is a debug message')
#logging.info('This is an info message')
#logging.warning('This is a warning message')
#logging.error('This is an error message')
#logging.critical('This is a critical message')
#logging.error("Exception occurred", exc_info=True)


# url = 'https://www.youtube.com/watch?v=e0JSLTXOrIc'
# start_time = '00:20:00'
# duration = '00:01:00'

def get_tennis_highlights(url,start_time=None, duration=None, sample_fps=3):

    os.system('rm -rf temp')
    os.system('mkdir temp')

    logging.basicConfig(filename='temp/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.info(current_time()+':'+'Downloading video')

    try:
        os.system('youtube-dl -f 18 '+url+' --output temp/temp.mp4')
        os.system('youtube-dl -f best '+url+' --output temp/temp_best.mp4')
    except:
        try:
            os.system('youtube-dl -f 134 '+url+' --output temp/temp.mp4')
            os.system('youtube-dl -f best '+url+' --output temp/temp_best.mp4')
        except:
            logging.error(current_time()+':'+'Unable to download video')


    logging.info(current_time()+':'+'Cutting video between timestamps')
    try:
        os.system('ffmpeg -ss '+start_time+'  -i temp/temp.mp4 -t '+duration+' -c copy temp/temp_clipped.mp4')
        os.system('ffmpeg -ss '+start_time+'  -i temp/temp_best.mp4 -t '+duration+' -c copy temp/temp_best_clipped.mp4')
    except:
        os.system('cp temp/temp.mp4 temp/temp_clipped.mp4')
        os.system('cp temp/temp_best.mp4 temp/temp_best_clipped.mp4')
        logging.error(current_time()+':'+'Unable to crop video as specified')

    try:
        os.system('mkdir temp/temp_images')
    except:
        logging.info(current_time()+':'+'temp/temp_images already exists')

    os.system('ffmpeg -i temp/temp_clipped.mp4 -r '+str(sample_fps)+' temp/temp_images/output_%04d.png')
    
    #####  AUDIO ARRAY EXTRACTION ######

    freq = 4410
    audio_array = audio_to_array('temp/temp_clipped.mp4',4410)

    logging.info(current_time()+':'+'Extracting Poses')
    cwd = os.getcwd()
    os.chdir(f'{cwd}/AlphaPose')
    os.system('python demo.py --indir ../temp/temp_images/ --outdir ../temp --conf 0.5 --nms 0.45 --sp --detbatch 2')
    os.chdir(cwd)

    logging.info(current_time()+':'+'Data Preprocessing')
    df = pd.read_json('temp/alphapose-results.json')
    df['clip']=[np.floor(int(i.split('.')[0].split('_')[-1])) for i in df.image_id]
    df['normalized_tuples'] = df.keypoints.apply(normalize_tuples)
    df['normalized_keypoints'] = df.keypoints.apply(normalize_keypoints)
    df['width'] = df.keypoints.apply(get_width)
    df['height'] = df.keypoints.apply(get_height)
    df['angle_at_leftelbow'] = df.keypoints.apply(get_angle_at_joint, args=('LShoulder','LElbow','LWrist'))
    df['angle_at_rightelbow'] = df.keypoints.apply(get_angle_at_joint, args=('RShoulder','RElbow','RWrist'))
    df['angle_at_leftshoulder'] = df.keypoints.apply(get_angle_at_joint, args=('LHip','LShoulder','LElbow'))
    df['angle_at_rightshoulder'] = df.keypoints.apply(get_angle_at_joint, args=('RHip','RShoulder','RElbow'))
    df['angle_at_leftknee'] = df.keypoints.apply(get_angle_at_joint, args=('LHip','LKnee','LAnkle'))
    df['angle_at_rightknee'] = df.keypoints.apply(get_angle_at_joint, args=('RHip','RKnee','RAnkle'))
    df['angle_at_hip'] = df.keypoints.apply(get_angle_at_hip)
    df['min_x'] = df.keypoints.apply(get_min_x)
    df['max_x'] = df.keypoints.apply(get_max_x)
    df['min_y'] = df.keypoints.apply(get_min_y)
    df['max_y'] = df.keypoints.apply(get_max_y)
    df['is_person_standing'] = df.keypoints.apply(is_person_standing_straight)

    df=df.sort_values(by=['image_id', 'height'],ascending=False).drop_duplicates(['image_id'])

    #df['height_rank']=df.groupby(['clip','image_id']).height.rank(ascending=False)
    #df = df[df['height_rank']>=1][df['height_rank']<=2]

    X_mat1 = np.vstack( (df.normalized_keypoints))
    X_mat2 = np.matrix(df[['angle_at_leftelbow','angle_at_rightelbow','angle_at_leftshoulder','angle_at_rightshoulder','angle_at_leftknee','angle_at_rightknee','angle_at_hip','width','height','min_x','min_y','max_x','max_y','is_person_standing']])
    X_mat = np.hstack((X_mat1,X_mat2))

    logging.info(current_time()+':'+'Model Prediction')
    print('Loading Model')
    clf = pickle.load(open('tennis/models/tennis_pose_play_v1.p','rb'))

    pred = clf.predict(X_mat)
    pred_proba = clf.predict_proba(X_mat)

    df['pred']= pred
    df['pred_proba']= pred_proba[:,1]
    res = df.groupby(['clip']).pred_proba.mean()
    moving_res = [np.sum(res[i-sample_fps:i+sample_fps])/(2*sample_fps) for i in range(len(res))]

    print(res)
    print(moving_res)

    threshold = np.percentile(moving_res,50,interpolation='nearest')

    chosen_threshold=np.float64(0.3)
    indices = np.where(moving_res>=chosen_threshold)[0]

    #if clips are missing with small differences between start times, need to fill them up
    indices=list(indices)
    indices_new=[]
    for i in range(len(indices)-1):
        indices_new.append(indices[i])
        if (indices[i+1]-indices[i])==2:
            indices_new.append(indices[i]+1)
                            
    indices_new.append(indices[-1])


    groups = [list(group) for group in mit.consecutive_groups(indices_new)]

    try:                           
        log = {"url":url, "start_time":start_time, "duration":duration, "df":df, "sample_fps":sample_fps, "model":clf, "result":res, "moving_res":moving_res, "threshold":threshold, "indices":indices, "groups":groups}

    except:
        log = {"url":url, "df":df, "sample_fps":sample_fps, "model":clf, "result":res, "moving_res":moving_res, "threshold":threshold, "indices":indices, "groups":groups} #skipping start_time and duration
        
        
    pickle.dump(log,open('temp/log.p','wb'))
        
    ###########################################################################################################################################


    logging.info(current_time()+':'+'Output file generation')
    os.system('mkdir temp/temp_clips')

    f= open("clipslist.txt","w+")

    prev_group=[- 1.0*(sample_fps),- 1.0*(sample_fps)] # amazing hack that i am not going to explain

    applause_meter=[]
    length_meter=[]

    for group in groups:        
        if len(group)>2*sample_fps:
            
            start_frame = group[0]  
            start_frame_adjusted = start_frame - 1.0*(sample_fps) # padding one second before
            start_frame_adjusted = max(start_frame_adjusted,prev_group[-1]+1.0*(sample_fps)) #making sure there is no overlap
            
            duration_frames = group[-1]-group[0]
            duration_frames_adjusted = duration_frames+1.0*(sample_fps) # padding one second after
            duration_frames_adjusted = min(duration_frames_adjusted, max(res.index)) #making sure output does not overshoot orig video duration
            
            start_time = frame_to_timestamp(start_frame_adjusted, sample_fps)
            duration = frame_to_timestamp(duration_frames_adjusted, sample_fps)
            os.system('ffmpeg -y -ss '+start_time+' -i temp/temp_clipped.mp4 -strict -2 -t '+duration+' temp/temp_clips/out'+str(group[0])+'.mp4')
            f.write("file "+"temp/temp_clips/out"+str(group[0])+".mp4\n")

            ##audio part
        
            secs = int(group[-1]/sample_fps)
            audio_array_next_5_secs = audio_array[freq*secs:freq*(secs+5)]
            applause_meter_clip = np.std(audio_array_next_5_secs)
            applause_meter.append((group[0], applause_meter_clip))
            length_meter.append((group[0], duration_frames))
        
        prev_group=group

    f.close()


    os.system('ffmpeg -f concat -safe 0 -i clipslist.txt -c copy temp/output.mp4')
    #os.system('ffmpeg -i temp/output.mp4 -strict -2 -filter:v "setpts=0.5*PTS" temp/output_spedup.mp4')
    ###########################################################################################################################################


    #ffmpeg -y -i output_spedup.mp4 -vf drawtext="text='play': fontcolor=black: fontsize=24: box=1: boxcolor=white@0.8: boxborderw=5: x=(w-text_w)/2: y=(text_h)/1.1" -codec:a copy output_with_label.mp4

    rand=int(time.time())
    os.system('mkdir results/run_'+str(rand))

    ######################################
    #####  Clips ordered by applause meter

    for i in applause_meter:
        print(i[0],i[1])

    order = np.argsort([i[1] for i in applause_meter])
    order_clips = [applause_meter[i][0] for i in order]

    loudest_clip = 'temp/temp_clips/out'+str(order_clips[-1])+'.mp4'
    os.system('cp '+loudest_clip+' temp/loudest.mp4') 

    f= open("loudlist.txt","w+")
    os.system('mkdir temp/top_10_clips')

    for i in reversed(order_clips[-10:]):
        os.system(f'mv temp/temp_clips/out{i}.mp4 temp/top_10_clips/')
        f.write("file "+"temp/temp_clips/out"+str(i)+".mp4\n")
        
    f.close()

    os.system('mkdir temp/output/')
    os.system('mv temp/output.mp4 temp/output/')
    os.system('mv temp/top_10_clips/ temp/output/')
    os.chdir(f'{cwd}/temp')
    os.system(f'zip -r output.zip output/')
    os.chdir(cwd)


    log['order_clips'] = order_clips
    log['applause_meter'] = applause_meter
    log['length_meter'] = length_meter
    pickle.dump(log,open('temp/log.p','wb'))

    #Manoj: Adding directory to identify latest dir
    #os.system('rm -r results/latest1/')
    #Anvesh: Removed folder itself instead of files to avoid permission issue
    #os.system('mkdir results/latest1')

    #os.system('rm clipslist.txt')

    os.system('cp -rf temp/* results/run_'+str(rand))
    #os.system('mv temp/* results/latest1')
    #os.system('rm -r temp')
    print(threshold)
    print('Completed the generation of the output video')

    return rand
    ###########################################################################################################################################

if __name__=="__main__":
    parser  = argparse.ArgumentParser()

    parser.add_argument('-l', '--url', help='Youtube url')
    #parser.add_argument('-s', '--start_time', help='Start time')
    #parser.add_argument('-d', '--duration', help='Duration')

    args = parser.parse_args()
    run_name = get_tennis_highlights(args.url)
    print(run_name)