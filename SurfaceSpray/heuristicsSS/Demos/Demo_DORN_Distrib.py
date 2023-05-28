import random
import copy
import math
import numpy as np


from enum import Enum

from ...utilsSS.Actions import *
from aima3.search import Problem as aimaProblem


class Demo_Dist_Ov_Rot_Distrib_V3(aimaProblem):

    def __init__(self, rules_, bbox, initial, goal=None, ):
        super().__init__(initial, goal)
        self.rules = rules_
        self.bounding_box = bbox
        # Bounding box magnitudes
        self.half_bounding_size_x = (bbox[4][0] - bbox[0][0])/2.0
        self.half_bounding_size_y = (bbox[2][1] - bbox[0][1])/2.0
        self.half_bounding_size_z = (bbox[1][2] - bbox[0][2])/2.0

    def getVertexBBoxLimits(self, vertex):
        """
        Returns the limits of the bounding box
        """
        max_X = vertex[0] + self.half_bounding_size_x
        min_X = vertex[0] - self.half_bounding_size_x
        max_Y = vertex[1] + self.half_bounding_size_y
        min_Y = vertex[1] - self.half_bounding_size_y
        max_Z = vertex[2] + self.half_bounding_size_z
        min_Z = vertex[2] - self.half_bounding_size_z

        return max_X, min_X, max_Y, min_Y, max_Z, min_Z

    def boundingBoxOverlapping(self, verA, verB):
        """
        Checks is the bounding box of Vertex A and Vertex B are overlapping

        Returns True or False
        """
        # Vertex B limits
        max_B_X, min_B_X, max_B_Y, min_B_Y, max_B_Z, min_B_Z = self.getVertexBBoxLimits(
            verB)

        # Overlap Condition
        if (verA[0] >= min_B_X and verA[1] <= max_B_X and
           verA[2] >= min_B_Y and verA[3] <= max_B_Y and
           verA[4] >= min_B_Z and verA[5] <= max_B_Z):
            return True

        return False

    def checkRestrictions(self, state, indexVertex):
        """
        Checks all restrictions by rules.

        state.vertices : array (1, 3) -> [position(vector), normal(vector), vertexUsed(boolean)] 

        indexVertex : actual vertex 

        Returns if all have passed. 
        """
        # If vertex already in use
        if (state.vertices_[indexVertex][2]):
            return False

        # Vertex we potentially want to place an object on.
        pCandidate = state.vertices_[indexVertex][0]

        rotation = self.rotate_to_vertex_normal(state.vertices_[indexVertex][1])
        # Random rotation applied to the object
        rotation += self.random_step_rotation()

        if (not self.rules.overlap):
            # Vertex A limits
            max_X, min_X, max_Y, min_Y, max_Z, min_Z = self.getVertexBBoxLimits(
                pCandidate)

            vertex_bbox_limits = (max_X, min_X, max_Y, min_Y, max_Z, min_Z)

        i = 0
        satisfiesRestrictions = True

        while (i < len(state.actionsApplied_) and satisfiesRestrictions == True):
            # Access vertices that has an object on it.
            indexVertex = state.actionsApplied_[i].indexVertex
            vertexInUse = state.vertices_[indexVertex][0]

            # Check bounding box overlap if needed
            if (not self.rules.overlap):
                satisfiesRestrictions = not self.boundingBoxOverlapping(
                    vertex_bbox_limits, vertexInUse)

            # Calculates distance between 2 tridimensional points.
            distance = math.sqrt((vertexInUse[0]-pCandidate[0])**2 + (
                vertexInUse[1]-pCandidate[1])**2 + (vertexInUse[2]-pCandidate[2])**2)
            # Compares if distance is lesser or equals to minimum distance.
            satisfiesRestrictions = satisfiesRestrictions and distance >= self.rules.distance_between_items

            i += 1

        return satisfiesRestrictions, rotation

    def actions(self, state):
        """
        Defines possible vertices in current state.

        state.vertices : array (1, 3) -> [position(vector), normal(vector), vertexUsed(boolean)] 

        Returns an array of indices, indicating which indices you can place an object on. 
        """
        possibleActions = []

        sizeV = len(state.vertices_)

        # Iterate over each state vertex checking if this vertex has a object on it, otherwise
        # it'll be considered as an action. (An object can be placed on it)
        # remaining = self.goal.objectsPlaced_ - state.objectsPlaced_
        remaining = 1

        randomIndices = random.sample(range(sizeV), sizeV)
        j = 0
        while (remaining > 0 and j < sizeV):
            i = randomIndices[j]

            satisfiesRestrictions, rotation = self.checkRestrictions(state, i)

            if (satisfiesRestrictions):
                j = 0
                
                # Check that is not a vertex that is already used 
                while (j < len(possibleActions) and (possibleActions[j].indexVertex != i)):
                    j += 1

                if (j < len(possibleActions) or len(possibleActions) == 0):
                    remaining -= 1
                    action = Actions(i, rotation)
                    possibleActions.append(action)

            j += 1

        if len(possibleActions) == 0:
            print('Could not find any vertex that satifies all rules.')

        return possibleActions


    def random_step_rotation(self):
        precision = 100.0

        rang_x = (int)(self.rules.rotation_range[0] * precision)
        rang_y = (int)(self.rules.rotation_range[1] * precision)
        rang_z = (int)(self.rules.rotation_range[2] * precision)

        step_x = (int)(self.rules.rotation_steps[0] * precision)
        step_y = (int)(self.rules.rotation_steps[1] * precision)
        step_z = (int)(self.rules.rotation_steps[2] * precision)

        rot_x = 0
        rot_y = 0
        rot_z = 0

        if (self.rules.rotations[0] != 0):
            rot_x = random.randrange(-rang_x, rang_x, step_x)
        if (self.rules.rotations[1] != 0):
            rot_y = random.randrange(-rang_y, rang_y, step_y)
        if (self.rules.rotations[2] != 0):
            rot_z = random.randrange(-rang_z, rang_z, step_z)

        return ((rot_x/precision) * (math.pi/180.0), rot_y/precision * (math.pi/180.0), rot_z/precision * (math.pi/180.0))

    def result(self, state, action):
        """
        Returns a new state in which an action has been applied.
        """
        newState = copy.deepcopy(state)
        newState.vertices_[action.indexVertex][2] = True
        newState.objectsPlaced_ += 1
        newState.actionsApplied_.append(action)
        return newState

    def goal_test(self, state):
        """
        Returns if the number of placed objects so far is equal to number of objects defined as goal.
        """
        # numero de objetos pedidos, separacion de objetos, tal.

        # Chill down
        return state.objectsPlaced_ == self.goal.objectsPlaced_
        # return True

    def h(self, node):
        """ 
        Return the heuristic value for a given state. Default heuristic function used is 
        h(n) = difference between number of objects placed and number of objects to place.  
        """
        diff = self.goal.objectsPlaced_ - node.state.objectsPlaced_
        print(diff)
        return diff
