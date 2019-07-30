import pandas as pd
import numpy as np
import os
import math
import sys

coco_format ={   0:"Nose",
    1:"LEye",
    2:"REye",
    3:"LEar",
    4:"REar",
    5:"LShoulder",
    6:  "RShoulder",
    7:  "LElbow",
    8:  "RElbow",
    9:  "LWrist",
    10: "RWrist",
    11: "LHip",
    12: "RHip",
    13: "LKnee",
    14: "RKnee",
    15: "LAnkle",
    16: "RAnkle"}

coco_format_flip = {v:k for k,v in coco_format.items()}

def get_3_tuples(keypoints):
    tuples=[]
    for i in range(int(len(keypoints)/3)):
        tuples.append((keypoints[3*i],keypoints[3*i+1],keypoints[3*i+2]))
    return tuples

def get_min_x(keypoints):
    tuples = get_3_tuples(keypoints)
    xs = [i[0] for i in tuples]
    return np.min(xs)

def get_max_x(keypoints):
    tuples = get_3_tuples(keypoints)
    xs = [i[0] for i in tuples]
    return np.max(xs)

def get_min_y(keypoints):
    tuples = get_3_tuples(keypoints)
    ys = [i[1] for i in tuples]
    return np.min(ys)

def get_max_y(keypoints):
    tuples = get_3_tuples(keypoints)
    ys = [i[1] for i in tuples]
    return np.max(ys)

def get_width(keypoints):
    return get_max_x(keypoints)-get_min_x(keypoints)

def get_height(keypoints):
    return get_max_y(keypoints)-get_min_y(keypoints)


def normalize_tuples(keypoints):
    tuples = get_3_tuples(keypoints)
    width = get_width(keypoints)
    height = get_height(keypoints)
    xs = [i[0] for i in tuples]
    ys = [i[1] for i in tuples]
    centre = ((np.max(xs)+np.min(xs))/2,(np.max(ys)+np.min(ys))/2)
    for i in range(len(tuples)):
        tuples[i]=((tuples[i][0]-centre[0])/width,(tuples[i][1]-centre[1])/height,tuples[i][2])
    return tuples

def normalize_keypoints(keypoints):
    tuples = normalize_tuples(keypoints)

    return [i for tuple in tuples for i in tuple]

def get_part_position(bodypart, keypoints, normalize=True):
    tuples = get_3_tuples(keypoints)
    if normalize:
        tuples = normalize_tuples(keypoints)
    try:
        return tuples[coco_format_flip[bodypart]][0:2]
    except:
        print('Something wrong')
        
def get_angle_vector(v1,v2):
    x1=v1[0]
    y1=v1[1]
    x2=v2[0]
    y2=v2[1]
    angle = 180*(math.atan2(y1,x1)-math.atan2(y2,x2))/3.1417
    return abs(angle)

def get_angle_at_joint(keypoints, endpoint1='Nose', fulcrum='LHip', endpoint2='LAnkle'):
    
    endpoint1_position = get_part_position(endpoint1,keypoints)
    fulcrum_position = get_part_position(fulcrum,keypoints)
    endpoint2_position = get_part_position(endpoint2,keypoints)
    
    v1= tuple(np.subtract(endpoint1_position,fulcrum_position))
    v2= tuple(np.subtract(fulcrum_position,endpoint2_position))
                               
    return get_angle_vector(v1,v2)

def get_angle_at_lefthip(keypoints):
    return get_angle_at_joint(keypoints,'Nose','LHip','LAnkle')

def get_angle_at_righthip(keypoints):
    return get_angle_at_joint(keypoints,'Nose','RHip','RAnkle')

def get_angle_at_hip(keypoints):
    left_angle = get_angle_at_lefthip(keypoints)
    right_angle = get_angle_at_righthip(keypoints)
    
    return left_angle + right_angle

def is_person_standing_straight(keypoints):
    if get_angle_at_hip(keypoints)<60:
        return 1
    else:
        return 0
    
def download_video_from_youtube(url, start_time=None, duration=None):
    
    os.system('mkdir temp')
    try:
        os.system('youtube-dl -f 18 '+url+' --output temp/temp.mp4')
    except Exception as e:
        logging.error("Video Download Error:", exc_info=True)
    if start_time is not None and duration is not None:
        print('Cutting video between timestamps')
        os.system('ffmpeg -ss '+start_time+' -i temp/temp.mp4 -t '+duration+' -c copy temp/temp_clipped.mp4')
    else:
        os.system('cp temp/temp.mp4 temp/temp_clipped.mp4')
    