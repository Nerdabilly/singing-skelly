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

It's important to note here that we won't be using Skelly's internal speaker - not only is it low quality, but if you're running a LOR show you probably have much better options for sound, and we really just want the jaw movement to sync with the vocals. 

One of the main issues with standard use of the Ultra Skelly is that the jaw movements don't always sync predictably - they have been known to sync to drums or other rhythm tracks, background vocals, other loud noises in the track, etc. To avoid this (and to save space on Skelly's relatively small memory) we need to extract only the vocal tracks from each song you want to synchronize. I used [Audacity](https://www.audacityteam.org/) with the [OpenVINO AI Effects](https://www.audacityteam.org/download/openvino/) plugins - both are free and open-source and I wrote a Macro to extract the vocals and save them out as MP3s. 

If you don't want to go through all that, or you only have a few tracks to work with, there are easier ways - I've used [vocalremover.org](https://vocalremover.org/) with decent results as well. 

**Note** these AI methods aren't 100% reliable, so it's a good idea to listen to the extracted vocal tracks and make sure they don't have any extraneous stuff like stray instruments, background vocals, noise, etc. If they do, they are easy to mute in Audacity (select the offending portion and Ctrl-L to mute it)

## Uploading the tracks to Skelly 

Another issue with the default Skelly app is that it doesn't allow tracks longer than 30 seconds. This makes sense, the onboard memory is limited and BLE transfer speeds can be very slowly. This is where the original [Ultra Skelly App Tools](https://github.com/tinkertims/SVI-Ultra-Skelly-Tools) comes in - using the [Web-based app](https://tinkertims.github.io/skelly/) we can upload full length tracks. The app will complain, but I didn't have any issues doing that. I also found it performed a little faster by downloading it from the source repo and running it off of `localhost`, but the hosted version is fine too. I do recommend checking the "Convert to device format (MP3, 8 kHz mono)" option as that speeds up the transfer and uses less space. 

I'd also recommend previewing them through the Skelly app or the web player - you want to make sure the jaw movement looks good. 

You can also play/pause them from the Command Prompt if you don't want to mess around with connecting/disconnecting the Skelly once you've completed the next step. 

```
python "C:\Users\path\to\this\project\ble_send.py" playpause --serial 15 --action 0
```
(If you're sending `action 0` to pause the playback, then the `serial` parameter doesn't actually matter here - it will pause whatever file is playing.)


## Connect the show player computer to Skelly using BLE

Here's where things get tricky - you need to get the Hardware ID of your Skelly and plug it into `ble_core.py`. To help with this, use the included `ble_scanner.py`. You may have to do a `pip install bleak` first if you haven't already. 

_Make sure the Skelly isn't connected to anything else when you do this! Disconnect from the SVI Decor app, the Ultra Skelly tools app, or anything else you may have connected him to._

```
python ble_scanner.py
```

This will show a list of all the nearby Bluetooth devices. Look for one that looks like this:

```
Name: Animated Skelly, Address: 12:34:56:78:90:AP
```

Copy the Address from this list and paste the value into `BLE_DEVICE_ADDRESS` in `ble_core.py`

Now, you should be able to connect to the Skelly:

```
python -m ble_daemon
```

(I don't know why, but my system complained when I didn't run it as a module. YMMV)

## 👇👇👇 SUPER IMPORTANT!! 👇👇👇
You **must** have the `ble_daemon` script running in a Command Prompt window while the LOR player runs - it's what keeps the connection active and sends the Bluetooth commands back and forth to Skelly. Without it, this just won't work and you'll probably see a lot of weird errors and strange behavior. 

## Send a Windows system command to tell Skelly what song to play

This is what ties it all together - each sequence will start by telling Skelly what vocal track to play. Again, make sure you have the **Advanced** Light-O-Rama license for this - you won't have the ability to use Windows system commands if you don't. 

To add the command to your LOR sequence, open a sequence in the Light-O-Rama sequencer software and click on **Sequence**, then  **Windows Command**. 

From there, you can select the `.cmd` file to start communicating with Skelly. There's an example in the `commands` folder. 

**IMPORTANT!** There needs to be some bi-directional communication for this to work. Unless Skelly and the LOR player are playing at the _exact same time_, the synchronization will be off and it will look stupid and be annoying. And that's where this gets a little more complicated - everything from network issues to Skelly's slow chip can cause this to not work. To compensate for this, we can wait for Skelly to send a notification that he has started playing the vocal track, and then continue playing the sequence. 

### That's where the Light-O-Rama REST API comes in. 

You need to enable the LOR REST API in order to synchronize Skelly. To do this, open the LOR Control Panel, click Settings, then Integration, and turn on the REST API option. You shouldn't have to anything else here, but make sure the Port for the LOR REST API is **different** from the `SERVER_PORT` variable at the top of `ble_daemon.py` 


The basic flow is:

1. When a sequence starts, the sequence's Windows command calls the LOR REST API to pause the Show Player. 
1. The next step in the CMD file waits 1 second - this is necessary to avoid too many calls at once to the LOR REST API
1. The CMD file calls the Python script telling Skelly to play the vocal track
1. Skelly transmits saying the file has started playing
1. The Python script receives the command and sends a call to the LOR REST API to resume playing the sequence. 

## Playing the right file 

Remember **each** sequence needs its own CMD file to play the associated vocal track on Skelly. Duplicate the example file for each sequence and change the `serial` parameter on the command to `ble_send.py` to match the index of the vocal track. You can get this list on the [Skelly BLE Controller](https://tinkertims.github.io/skelly/) web app (it's the number in the first column under the file list). It's a good idea to run the sequence in the Sequencer with the CMD file linked up to make sure it's starting the right file. If it isn't see, use `ble_send.py playpause --serial 15 --action 0` to stop playback. 

**Note:** If you're previewing in the Sequencer, the sync will probably be off. This is because it's waiting for the REST API calls to sync up. To get a more accurate preview, add your sequence to a Show in the LOR Control Panel and play the show (you don't actually need to be connected to a LOR controller to do this!)

**Also Note:** LOR Sequences **will not** dynamically update if a CMD file changes. If you need to change _any_ of the parameters in a linked CMD file, make the changes, and then go back into the Sequencer and link the CMD file again using the "New Command" option. 

---

And that's it! Complicated, not guaranteed to work and a pretty niche use case, but if you like it, let me know!

Happy Haunting! 