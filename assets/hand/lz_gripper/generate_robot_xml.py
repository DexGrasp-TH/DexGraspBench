import os
import sys
import xml.etree.ElementTree as ET

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.utils_mjcf import (
    find_element_index,
    find_elements,
    find_parent,
    indent,
    new_element,
)
from utils.utils_urdf import urdf_to_xml

if __name__ == "__main__":
    urdf_source_path = "assets/lz_gripper/lz_gripper_body.urdf"
    urdf_save_path = urdf_source_path
    xml_path = "assets/lz_gripper/lz_gripper_raw.xml"
    gravcomp: bool = True

    # ------------------ modify the urdf file ------------------
    with open(urdf_source_path, "r") as file:
        content = file.read()

    # the meshes and relpaths are in correct format, no need to change

    os.makedirs(os.path.dirname(urdf_save_path), exist_ok=True)
    with open(urdf_save_path, "w") as file:
        file.write(content)

    # ------------------ convert the urdf to xml ------------------
    urdf_to_xml(urdf_save_path, xml_path)
    print("Convert the urdf file to xml file.")

    # # ------------------ delete the temp urdf file ------------------
    # os.remove(urdf_save_path)
    # print("Delete the temp urdf file.")

    # ------------------ process the xml file ------------------
    # robot body xml file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # add 'class' attribute to the robot arm in the future

    # add 'gravcomp' to the robot bodies
    if gravcomp:
        bodies = find_elements(root, tags="body", return_first=False)
        for body in bodies:
            body.set("gravcomp", "1")
        print("Add 'gravcomp = 1' attribute to the robot.")

    # replace the collision mesh for the robot arm in the future

    shadow_joint_lst = [
        "thumb_joint1", "thumb_joint2", "thumb_joint3",
        "index_joint1", "index_joint2",
        "middle_joint1", "middle_joint2",
        "ring_joint1", "ring_joint2",
        "little_joint1", "little_joint2",
    ]

    # add 'class' attribute to the hand joints
    joints = find_elements(root, tags="joint", return_first=False)
    for joint in joints:
        if joint.get("name") in shadow_joint_lst:
            joint.set("class", "hand_joint")
            # delete actuatorfrcrange and damping
            if "actuatorfrcrange" in joint.attrib:
                del joint.attrib["actuatorfrcrange"]
            if "damping" in joint.attrib:
                del joint.attrib["damping"]
    print("Add 'class' attributes to the hand joints.")

    # add 'class' attributes to the visual and collision geoms for the shadow hand
    geoms = find_elements(root, tags="geom", return_first=False)
    for geom in geoms:
        if "contype" not in geom.attrib:
            name = geom.get("mesh")
            geom.set("class", "plastic_collision")
        elif "contype" in geom.attrib and "conaffinity" in geom.attrib:
            if geom.get("contype") == "0" and geom.get("conaffinity") == "0":
                name = geom.get("mesh")
                geom.set("class", "plastic_visual")
    print("Add 'class' attributes to the visual and collision geoms for the shadow hand.")

    # add float wrist joints (3 slide joints for translation, and 3 hinge joints for rotation)
    # make sure the slide joints are before the hinge joints
    palm = find_elements(root, tags="body", return_first=True, attribs={"name": "base_link"})
    if palm is not None:
        # add hinge joints
        hinge_joints = [
            new_element("joint", name="palm_joint4", axis="1 0 0"),
            new_element("joint", name="palm_joint5", axis="0 1 0"),
            new_element("joint", name="palm_joint6", axis="0 0 1"),
        ]
        for joint in reversed(hinge_joints):
            joint.set("class", "palm_hinge")
            palm.insert(0, joint)

        # add slide joints
        slide_joints = [
            new_element("joint", name="palm_joint1", axis="1 0 0"),
            new_element("joint", name="palm_joint2", axis="0 1 0"),
            new_element("joint", name="palm_joint3", axis="0 0 1"),
        ]
        for joint in reversed(slide_joints):
            joint.set("class", "palm_slide")
            palm.insert(0, joint)  # insert before the first geom

        print("Add float wrist joints to the palm body.")


    # save the xml file
    indent(root)  # format the xml
    tree.write(xml_path, encoding="utf-8")
    print(f"Save {xml_path}.")
