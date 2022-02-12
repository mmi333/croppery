pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.9/index.html
git clone https://github.com/facebookresearch/Detic.git --recurse-submodules
pip install -r requirements.txt
mv Detic/* .
git clone https://github.com/xingyizhou/CenterNet2
mv CenterNet2/projects/CenterNet2/centernet .