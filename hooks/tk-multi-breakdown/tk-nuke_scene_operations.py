# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import nuke
import hiero.core
from hiero.core import newProject
from hiero.core import BinItem
from hiero.core import MediaSource
from hiero.core import Clip
from hiero.core import Sequence
from hiero.core import VideoTrack
from tank import Hook
import sgtk
logger = sgtk.platform.get_logger(__name__)


class BreakdownSceneOperations(Hook):
    """
    Breakdown operations for Nuke.

    This implementation handles detection of Nuke read nodes,
    geometry nodes and camera nodes.
    """

    def scan_scene(self):
        """
        The scan scene method is executed once at startup and its purpose is
        to analyze the current scene and return a list of references that are
        to be potentially operated on.

        The return data structure is a list of dictionaries. Each scene reference
        that is returned should be represented by a dictionary with three keys:

        - "node": The name of the 'node' that is to be operated on. Most DCCs have
          a concept of a node, path or some other way to address a particular
          object in the scene.
        - "type": The object type that this is. This is later passed to the
          update method so that it knows how to handle the object.
        - "path": Path on disk to the referenced object.

        Toolkit will scan the list of items, see if any of the objects matches
        any templates and try to determine if there is a more recent version
        available. Any such versions are then displayed in the UI as out of date.
    
        """

        reads = []

        myProject = hiero.core.projects()
        for i in myProject :
           
            #-------------------Defiene Hiero var----------------
            myPro = i
            clipsBin = myPro.clipsBin()
            clips = clipsBin.clips()
            #-------------------Defiene Hiero var----------------
            
            #-------------------------Pull Hiero Path in reads--------------------------
            for clip in clips:
                zec = clip.activeItem()
                mediaSource = zec.mediaSource()
                files = mediaSource.fileinfos()
                for file in files:
                    path = file.filename().replace("/", os.path.sep)
                    reads.append( {"node": zec, "type": "Clip", "path": path})
            
    


        # first let's look at the read nodes
        for node in nuke.allNodes("Read"):

            node_name = node.name()

            # note! We are getting the "abstract path", so contains
            # %04d and %V rather than actual values.
            path = node.knob('file').value().replace("/", os.path.sep)

            reads.append( {"node": node_name, "type": "Read", "path": path})
            logger.debug("inside my code, i can log like thiszzzzz")

        # then the read geometry nodes    
        for node in nuke.allNodes("ReadGeo2"):
            node_name = node.name()
            
            path = node.knob('file').value().replace("/", os.path.sep)
            reads.append( {"node": node_name, "type": "ReadGeo2", "path": path})
        
        # then the read camera nodes    
        for node in nuke.allNodes("Camera2"):
            node_name = node.name()
            
            path = node.knob('file').value().replace("/", os.path.sep)
            reads.append( {"node": node_name, "type": "Camera2", "path": path})

        return reads


    def update(self, items):
        """
        Perform replacements given a number of scene items passed from the app.

        Once a selection has been performed in the main UI and the user clicks
        the update button, this method is called.

        The items parameter is a list of dictionaries on the same form as was
        generated by the scan_scene hook above. The path key now holds
        the that each node should be updated *to* rather than the current path.
        """

        engine = self.parent.engine

        node_type_list = ["Read", "ReadGeo2", "Camera2"]
        node_type_list_s = ["Clip"]
        for i in items:
            node_name = i["node"]
            node_type = i["type"]
            new_path = i["path"]

            if node_type in node_type_list :
                engine.log_debug("Node %s: Updating to version %s" % (node_name, new_path))
                node = nuke.toNode(node_name)
                # make sure slashes are handled correctly - always forward
                new_path = new_path.replace(os.path.sep, "/")
                node.knob("file").setValue(new_path)

            if node_type in node_type_list_s :
                engine.log_debug("Node %s: Updating to version %s" % (node_name, new_path))
                clip = node_name
                # make sure slashes are handled correctly - always forward
                new_path = new_path.replace(os.path.sep, "/")
                clip.reconnectMedia(new_path)

