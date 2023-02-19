# Backend--Django--Developer

This is simple API that allows any user to upload an image in PNG or JPG format.
It is created using Django REST Framework.

You can:
* upload image
* list your images

## Setup
To run this project you need to install all dependencies in requirements.txt:
```
$ pip install django
$ pip install djangorestframework
$ pip install djangorestframework-simplejwt
$ pip install Pillow
$ pip install PyJWT
$ pip install sorl-thumbnail==11.12
```

or using git clone
```
git clone https://github.com/patrinhoo/Backend--Django--Developer
```

## There are 3 account tiers:  
* Basic:  
thumbnail 200px in height

* Premium:  
thumbnail 200px in height  
thumbnail 400px in height
original image  

* Enterprise:  
thumbnail 200px in height  
thumbnail 400px in height
original image  
fetch a link to image that expires  

## Short Demonstration 
* List your images and upload new image  
![ezgif com-video-to-gif](https://user-images.githubusercontent.com/81069467/219980727-75123234-a75b-453c-96de-3f26245f5aff.gif)
  
* Get original image  
![ezgif com-video-to-gif (1)](https://user-images.githubusercontent.com/81069467/219980758-52fcf812-4502-437e-90cc-4a4a0df18312.gif)
  
* Get thumbnail  
![ezgif com-video-to-gif (2)](https://user-images.githubusercontent.com/81069467/219980782-45c48756-2d40-4295-a8ca-ac36630c1c89.gif)
  
* Get and use link that expires after specified amount of time
![ezgif com-video-to-gif (3)](https://user-images.githubusercontent.com/81069467/219980850-eb95265d-8ea7-41f2-9b8a-2dde84bbace8.gif)
  
* Use link that expired
![ezgif com-video-to-gif (4)](https://user-images.githubusercontent.com/81069467/219980855-b3d9143c-19c7-435d-b755-59c48865930c.gif)
  
