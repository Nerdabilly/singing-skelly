# Singing Skelly

Borrows heavily from https://github.com/tinkertims/SVI-Ultra-Skelly-Tools 

## This is very much a work in progress and not guaranteed to work

Synchronizes the [SVI App Controlled Ultra Skeleton](https://www.homedepot.com/p/Home-Accents-Holiday-6-5-ft-Grave-Bones-Animated-LED-App-Controlled-Ultra-Skelly-with-LifeEyes-LCD-Eyes-H23-25SV24690/333508046)
from Home Depot with a Light-O-Rama show

## Intro

I wanted my Ultra App Skelly to sing along with the show sequences in my Light-O-Rama synchronized light show. He wasn't originally set up for this, but luckily someone smarter than me set up a [repo](https://github.com/tinkertims/SVI-Ultra-Skelly-Tools) with a lot of the BLE protocol reverse-engineered and made a nice little web app to control Skelly. Using this (with the help of ChatGPT) I was able to put this utility together and get Skelly to perform along with the show.

## What You'll Need

1. An App Controlled Ultra Skeleton (duh)
1. A Light-O-Rama system with at least a **license level of Advanced** - this system relies on LOR's ability to launch Windows commands at the start of a sequence, and this feature is not available in license levels lower than Advanced. 
1. Python installed on the LOR host system - you need to also install the `bleak` and `requests` libraries 
1. (Optional, but helpful) [Audacity](https://www.audacityteam.org/) with the [OpenVINO AI Effects](https://www.audacityteam.org/download/openvino/) plugins installed 

```
pip install bleak
pip install requests
```

## How it works

The basic process is:

1. Get the vocal tracks you want Skelly to sing
1. Upload them to Skelly 
1. Connect the show player computer to Skelly using BLE
1. When a sequence plays, send a Windows system command to tell Skelly what song to play

## Getting the Vocal Tracks 

One of the main issues with standard use of the Ultra Skelly is that the jaw movements don't always sync predictably - they have been known to sync to drums or other rhythm tracks, background vocals, other loud noises in the track, etc. To avoid this (and to save space on Skelly's relatively small memory) we need to extract only the vocal tracks from each song you want to synchronize. I used [Audacity](https://www.audacityteam.org/) with the [OpenVINO AI Effects](https://www.audacityteam.org/download/openvino/) plugins - both are free and open-source and wrote a Macro to extract the vocals and save them out as MP3s. 

If you don't want to go through all that, or you only have a few tracks to work with, there are easier ways as well - I've used [vocalremover.org](https://vocalremover.org/) with decent results as well. 

**Note** these AI methods aren't 100% reliable, so it's a good idea to listen to the extracted vocal tracks and make sure they don't have any extraneous stuff like stray instruments, background vocals, noise, etc. If they do, they are easy to mute in Audacity (select the offending portion and Ctrl-L to mute it)

## Uploading the tracks to Skelly 

Another issue with the default Skelly app is that it doesn't allow tracks longer than 30 seconds. This makes sense, the onboard memory is limited and BLE transfer speeds can be very slowly. This is where the original [Ultra Skelly App Tools](https://github.com/tinkertims/SVI-Ultra-Skelly-Tools) comes in - using the (Web-based app)[https://tinkertims.github.io/skelly/] we can upload full length tracks. The app will complain, but I didn't have any issues doing that.   