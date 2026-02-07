This Blender add-on is a collection of utilities developed for working with [*Darkest Hour: Europe '44-'45*](https://github.com/DarklightGames/DarkestHour) assets.

Supported Blender versions:
- 5.0+
- 4.5 LTS
- 4.2 LTS (should work, not tested)

# Installation
## Method 1: Extension repository (recommended)
>[!CAUTION]
>Make sure to uninstall any previous installations of this addon to avoid conflicts.

To add the repository:
1. Open Blender and go to `Edit -> Preferences -> Get Extensions -> Repositories`.
2. Add a new repository with the `+` button.
3. Copy and paste the following link into the `URL` field:
   ```md
   https://darklightgames.github.io/dlg_blender_addon/repository/
   ```
4. Turn on `Check for Updates on Startup` to enable automatic updates (optional).
5. Click `Create`

Once repository has been added, find `Darklight Games Animation Tools` and click `Install`.

## Method 2: Manual installation
1. Download the zip file from the latest [release page](https://github.com/DarklightGames/dlg_blender_addon/releases/latest).
2. Open Blender and go to `Edit -> Preferences -> Add-ons`.
3. Click the `Install...` button.
4. Select the downloaded zip and click `Install Add-on`.
5. Enable the newly added `Darklight Games Blender Tools`.


# Tools
## Retarget Actions

This tool is used to automate the proccess of importing animations from the game and transferring them onto a control rig.

>[!NOTE]
>This is not a general purpose retargetting tool and it's meant to only work with our specific setup.

<img width="344" height="370" alt="retarget-actions" src="https://github.com/user-attachments/assets/21450b52-a232-4497-8b85-02eeabb6e9e9" />

## Add Actions (NLA)
Allows adding actions to NLA tracks in batches. The actions are saved into groups for organizing and reuse.

<img width="275" height="190" alt="add-actions" src="https://github.com/user-attachments/assets/37c1f1b8-1004-4e6f-aac2-cb6c49ea83ea" />

## Add Markers (NLA)
Generates markers from selected strips in the NLA editor. 

<img width="275" height="186" alt="add-markers" src="https://github.com/user-attachments/assets/a3204800-ed49-49da-81bb-725c54b9214b" />
