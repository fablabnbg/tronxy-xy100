AppImage JailBreak
==================

Cura is shipped as an AppImage. This simplifies installation, but hinders plugin development.
One 'Extension' plugin included is the `PostProcessingPlugin` -- its description says:
'Extension that allows for user created scripts for post processing'.

Unfortunately the path where 'user created scripts' are loaded is hardcoded inside the 
AppImage. While cura runs, the path to the scripts directory is exposed as e.g.

`/tmp/.mount_hAQsmr/usr/bin/plugins/plugins/PostProcessingPlugin/scripts/`

The entire file system of an AppImage is per definition read-only. That means, it is 
not possible to develop scripts in that directory.

To add (or change) a script, the AppImage needs to be unpacked into an AppDir, then the change can be applied,
then re-packed as an AppImage.


Adding a user writable scripts directory
----------------------------------------

The following patch adds loading of scripts from an additional directory 

`$HOME/.config/cura/plugins/PostProcessingPlugin/scripts/`

This helps for developing a post processing script, as only a cura restart is needed to activate the new script, instead of building the AppImage.

```
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
wget https://github.com/AppImage/AppImageKit/releases/download/6/AppImageExtract_6-x86_64.AppImage
chmod a+x *.AppImage
sudo apt-get install appstream

AppImageExtract_6-x86_64.AppImage ~/bin/Cura-2.5.0.AppImage
(cd ~/Desktop/Cura-2.5.0.AppImage.AppDir; patch -p1 ) < user_plugins_dir.patch
appimagetool-x86_64.AppImage ~/Desktop/Cura-2.5.0.AppImage.AppDir ~/bin/Cura-2.5.0.user-scripts.AppImage
chmod a+x ~/bin/Cura-2.5.0.user-scripts.AppImage
```

For development of a new script you can now also inspect the contents of `Cura-2.5.0.AppImage.AppDir`.
Scripts placed in `$HOME/.config/cura/plugins/PostProcessingPlugin/scripts` are now loaded, whenever you restart cura.


Adding a script
---------------

The user_plugins_dir.patch is not needed when you only want to add a script. The procedure is:

```
AppImageExtract_6-x86_64.AppImage ~/bin/Cura-2.5.0.AppImage
cp RollerCoaster.py ~/Desktop/Cura-2.5.0.AppImage.AppDir/usr/bin/plugins/plugins/PostProcessingPlugin/scripts/
appimagetool-x86_64.AppImage ~/Desktop/Cura-2.5.0.AppImage.AppDir ~/bin/Cura-2.5.0.with-rc.AppImage
chmod a+x ~/bin/Cura-2.5.0.with-rc.AppImage
```

