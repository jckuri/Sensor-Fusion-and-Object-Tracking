# ---------------------------------------------------------------------
# Project "Track 3D-Objects Over Time"
# Copyright (C) 2020, Dr. Antje Muntzinger / Dr. Andreas Haja.
#
# Purpose of this file : Classes for track and track management
#
# You should have received a copy of the Udacity license together with this program.
#
# https://www.udacity.com/course/self-driving-car-engineer-nanodegree--nd013
# ----------------------------------------------------------------------
#

# imports
import numpy as np
import collections

# add project directory to python path to enable relative imports
import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import misc.params as params 

class Track:
    '''Track class with state, covariance, id, score'''
    def __init__(self, meas, id):
        print('creating track no.', id)
        M_rot = meas.sensor.sens_to_veh[0:3, 0:3] # rotation matrix from sensor to vehicle coordinates
        
        ############
        # TODO Step 2: initialization:
        # - replace fixed track initialization values by initialization of x and P based on 
        # unassigned measurement transformed from sensor to vehicle coordinates
        # - initialize track state and track score with appropriate values
        ############

        self.x = np.matrix([[49.53980697],
                        [ 3.41006279],
                        [ 0.91790581],
                        [ 0.        ],
                        [ 0.        ],
                        [ 0.        ]])
        self.P = np.matrix([[9.0e-02, 0.0e+00, 0.0e+00, 0.0e+00, 0.0e+00, 0.0e+00],
                        [0.0e+00, 9.0e-02, 0.0e+00, 0.0e+00, 0.0e+00, 0.0e+00],
                        [0.0e+00, 0.0e+00, 6.4e-03, 0.0e+00, 0.0e+00, 0.0e+00],
                        [0.0e+00, 0.0e+00, 0.0e+00, 2.5e+03, 0.0e+00, 0.0e+00],
                        [0.0e+00, 0.0e+00, 0.0e+00, 0.0e+00, 2.5e+03, 0.0e+00],
                        [0.0e+00, 0.0e+00, 0.0e+00, 0.0e+00, 0.0e+00, 2.5e+01]])
        self.state = 'confirmed'
        self.score = 0
        
        # PART 2
        z = np.ones((4, 1))
        z[:meas.sensor.dim_meas] = meas.z
        self.x = np.zeros((6, 1))
        self.x[:3] = (meas.sensor.sens_to_veh * z)[:3]        
        self.P = np.matrix([[9.0e-02, 0.0e+00, 0.0e+00, 0.0e+00,          0.0e+00,          0.0e+00],
                            [0.0e+00, 9.0e-02, 0.0e+00, 0.0e+00,          0.0e+00,          0.0e+00],
                            [0.0e+00, 0.0e+00, 6.4e-03, 0.0e+00,          0.0e+00,          0.0e+00],
                            [0.0e+00, 0.0e+00, 0.0e+00, params.sigma_p44, 0.0e+00,          0.0e+00],
                            [0.0e+00, 0.0e+00, 0.0e+00, 0.0e+00,          params.sigma_p55, 0.0e+00],
                            [0.0e+00, 0.0e+00, 0.0e+00, 0.0e+00,          0.0e+00,          params.sigma_p66]])
        self.state = 'initialized'
        self.score = 1. / params.window
        self.assignments = [1]
        
        ############
        # END student code
        ############ 
               
        # other track attributes
        self.id = id
        self.width = meas.width
        self.height = meas.height
        self.length = meas.length
        self.yaw = np.arccos(M_rot[0,0]*np.cos(meas.yaw) + M_rot[0,1]*np.sin(meas.yaw)) # transform rotation from sensor to vehicle coordinates
        self.t = meas.t

    def append_assignment_and_compute_score(self, assignment):
        self.assignments.append(assignment)
        last_assignments = self.assignments[-params.window:]
        #print('assignments={}, last_assignments={}'.format(self.assignments, last_assignments))
        print(f'last_assignments={last_assignments}')
        self.score = sum(last_assignments) / float(params.window)

    def set_x(self, x):
        self.x = x
        
    def set_P(self, P):
        self.P = P  
        
    def set_t(self, t):
        self.t = t  
        
    def update_attributes(self, meas):
        # use exponential sliding average to estimate dimensions and orientation
        if meas.sensor.name == 'lidar':
            c = params.weight_dim
            self.width = c*meas.width + (1 - c)*self.width
            self.length = c*meas.length + (1 - c)*self.length
            self.height = c*meas.height + (1 - c)*self.height
            M_rot = meas.sensor.sens_to_veh
            self.yaw = np.arccos(M_rot[0,0]*np.cos(meas.yaw) + M_rot[0,1]*np.sin(meas.yaw)) # transform rotation from sensor to vehicle coordinates
        
        
###################        

class Trackmanagement:
    '''Track manager with logic for initializing and deleting objects'''
    def __init__(self):
        self.N = 0 # current number of tracks
        self.track_list = []
        self.last_id = -1
        self.result_list = []
        
    def manage_tracks(self, unassigned_tracks, unassigned_meas, meas_list):  
        ############
        # TODO Step 2: implement track management:
        # - decrease the track score for unassigned tracks
        # - delete tracks if the score is too low or P is too big (check params.py for parameters that might be helpful, but
        # feel free to define your own parameters)
        ############
        
        # decrease score for unassigned tracks
        for i in unassigned_tracks:
            track = self.track_list[i]
            # check visibility    
            if meas_list: # if not empty
                print(f'Testing to decrease score. meas_list[0].sensor.name={meas_list[0].sensor.name}')
                if meas_list[0].sensor.in_fov(track.x):
                    # your code goes here
                    pass
                    track.append_assignment_and_compute_score(0)

        # delete old tracks   
        to_be_deleted = []
        for i in range(len(self.track_list)):
            track = self.track_list[i]
            P = track.P
            if (track.state == 'initialized' and track.score <= 0.01 and len(track.assignments) >= 4) or \
            (track.state == 'tentative' and track.score <= 0.2) or \
            (track.state == 'confirmed' and track.score <= 0.2) or \
            (P[0,0] > params.max_P or P[1,1] > params.max_P):
                to_be_deleted.append(track)
        for track in to_be_deleted:
            self.delete_track(track)                
        
        ############
        # END student code
        ############ 
        
        # initialize new track with unassigned measurement
        for j in unassigned_meas: 
            if meas_list[j].sensor.name == 'lidar': # only initialize with lidar measurements
                self.init_track(meas_list[j])
            
    def addTrackToList(self, track):
        self.track_list.append(track)
        self.N += 1
        self.last_id = track.id

    def init_track(self, meas):
        track = Track(meas, self.last_id + 1)
        self.addTrackToList(track)

    def delete_track(self, track):
        print('deleting track no.', track.id)
        self.track_list.remove(track)
        
    def handle_updated_track(self, track):      
        ############
        # TODO Step 2: implement track management for updated tracks:
        # - increase track score
        # - set track state to 'tentative' or 'confirmed'
        ############

        track.append_assignment_and_compute_score(1)
        if track.state == 'initialized' and track.score >= 0.5:
            track.state = 'tentative'
        if track.state == 'tentative' and track.score >= 0.8:
            track.state = 'confirmed'
        
        ############
        # END student code
        ############ 
