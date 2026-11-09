# STM32 Toolchain Installation

This guide covers installing **STM32CubeIDE** (Eclipse-based IDE with compiler, debugger and ST-LINK support) and **STM32CubeProgrammer** (standalone flashing/programming tool, GUI and CLI) on Windows 11 and Linux.

> **Version note:** At the time of writing, STM32CubeIDE is on the **2.x** series (v2.2.0 is the newest release I found) and STM32CubeProgrammer is on **2.2x** (docs for 2.23.0). Exact file names change with each release, so replace `x.y.z` below with the version you downloaded. Always check [st.com/stm32cubeide](https://www.st.com/stm32cubeide) and [st.com/stm32cubeprog](https://www.st.com/en/development-tools/stm32cubeprog.html) for the latest.

---

## 1. Before you start

### 1.1 Requirements

| Item | Recommendation |
|---|---|
| OS | Windows 11 (64-bit), or a recent 64-bit Linux (Ubuntu/Debian, Fedora/RHEL, or any distro using the generic installer) |
| Disk space | ~3 GB free for CubeIDE, plus extra for firmware packages; ~500 MB for CubeProgrammer |
| Privileges | Administrator (Windows) or `sudo` (Linux) |
| Internet | Needed to download installers and, later, device/firmware packages |
| ST account | A free **myST account** is required to download the installers |

### 1.2 Download the installers

1. Create or log in to a free account at [st.com](https://www.st.com).
2. Download from the official product pages:
   - **STM32CubeIDE:** <https://www.st.com/en/development-tools/stm32cubeide.html>
   - **STM32CubeProgrammer:** <https://www.st.com/en/development-tools/stm32cubeprog.html>
3. Pick the right package:

| Tool | Windows 11 | Linux |
|---|---|---|
| STM32CubeIDE | `STM32CubeIDE-Win` (Windows installer) | `STM32CubeIDE-Lnx` (generic `.sh`), `STM32CubeIDE-DEB` (Debian/Ubuntu), or `STM32CubeIDE-RPM` (Fedora/RHEL/SUSE) |
| STM32CubeProgrammer | `STM32CubeProgrammer-Win` (zip) | `STM32CubeProgrammer-Linux` (zip containing `SetupSTM32CubeProgrammer-x.y.z.linux`) |

> ST's download links require login and a license acceptance, so you can't fetch them with `wget`/`curl`. Download in a browser, then copy to your machine if needed.

### 1.3 Note on STM32CubeMX

Starting with STM32CubeIDE **2.0.0**, STM32CubeMX is **no longer integrated** into the IDE. If you want graphical pin/clock configuration and code generation, install **STM32CubeMX** separately from [st.com/stm32cubemx](https://www.st.com/en/development-tools/stm32cubemx.html) and open the generated project in CubeIDE (or use the CubeMX integration/extension that ST provides for your CubeIDE version).

---

## 2. Windows 11

### 2.1 Install STM32CubeIDE

1. Right-click the downloaded zip and choose **Extract All…**.
2. Run the installer (`st-stm32cubeide_x.y.z_..._x86_64.exe`) as Administrator: right-click → **Run as administrator**.
3. If **Windows SmartScreen** appears, click **More info → Run anyway** (the installer is signed by STMicroelectronics; verify the publisher).
4. Accept the license agreement.
5. Choose the install folder.
   - The default is typically `C:\ST\STM32CubeIDE_x.y.z`.
   - Keep the path **short and without spaces or non-ASCII characters** to avoid toolchain issues.
6. When prompted, **leave the driver/component options enabled**:
   - ST-LINK drivers
   - ST-LINK server
   - SEGGER J-Link drivers (only if you use J-Link probes)
7. Finish the installation. Launch **STM32CubeIDE** from the Start menu.
8. On first launch, choose a **workspace** folder (short path, no spaces, e.g. `C:\stm32_ws`).

### 2.2 Install STM32CubeProgrammer

1. Extract the downloaded zip.
2. Run `SetupSTM32CubeProgrammer_win64.exe` as Administrator.
3. Accept the license and choose an install path (default: `C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer`).
4. Keep the driver options ticked so the ST-LINK and USB DFU drivers get installed.
5. Finish and launch **STM32CubeProgrammer** from the Start menu.

> No separate Java installation is required for STM32CubeProgrammer (since v2.6.0).

### 2.3 Verify on Windows

Plug in an ST-LINK or a Nucleo/Discovery board over USB, then:

**STM32CubeProgrammer GUI:** select **ST-LINK** in the top-right dropdown and click **Connect**.

**Command line (PowerShell):**

```powershell
cd "C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin"
.\STM32_Programmer_CLI.exe -l
```

You should see your ST-LINK listed. To use the CLI from anywhere, add that `bin` folder to your **PATH** (Settings → System → About → Advanced system settings → Environment Variables).

**STM32CubeIDE:** use **File → New → STM32 Project**, pick your board/MCU, build, then run **Run → Debug** to confirm the probe is detected.

### 2.4 Windows troubleshooting

| Problem | Fix |
|---|---|
| ST-LINK not detected | Try another USB cable (data cable, not charge-only) and port. Reinstall the ST-LINK driver (`stsw-link009`, included in the CubeProgrammer `Drivers` folder). |
| Board in DFU mode not recognized | Install the STM32 DFU driver from the CubeProgrammer `Drivers\DFU_Driver` folder, then re-plug the board while holding BOOT0 high. |
| ST-LINK firmware outdated warning | In CubeProgrammer click **Firmware upgrade** next to the ST-LINK selector, or in CubeIDE use **Help → ST-LINK Upgrade**. |
| Antivirus blocks installer | Temporarily allow the installer or add an exception; re-download if the file is corrupted. |

---

## 3. Linux

The commands below use Ubuntu/Debian for package installs. Adapt them for Fedora (`dnf`) or Arch (`pacman`) as needed.

### 3.1 Install prerequisites

```bash
sudo apt update
sudo apt install -y unzip libusb-1.0-0 udev
```

STM32CubeProgrammer needs **libusb 1.0.12 or newer**.

### 3.2 Install STM32CubeIDE

Go to the folder containing your download and extract it:

```bash
cd ~/Downloads
unzip en.st-stm32cubeide_*.zip -d stm32cubeide-installer
cd stm32cubeide-installer
```

Choose **one** of the three methods.

#### Option A: Generic installer (works on any distro)

```bash
chmod +x st-stm32cubeide_*.sh
sudo ./st-stm32cubeide_*.sh
```

Follow the prompts: accept the license, choose the install path (default is under `/opt/st/stm32cubeide_x.y.z`), and accept the ST-LINK / J-Link component installs. Run with `sudo` so the udev rules and helper components can be installed.

#### Option B: Debian/Ubuntu (`.deb`)

The DEB package contains several `.deb` files (IDE plus helper components such as the ST-LINK server and udev rules). Install them with `apt` so dependencies resolve automatically:

```bash
sudo apt install ./st-*.deb
```

If some components fail or ask for license confirmation interactively, install them one at a time, in the order listed in ST's installation guide **UM2563**.

#### Option C: Fedora/RHEL/SUSE (`.rpm`)

```bash
sudo dnf install ./st-*.rpm
```

(On openSUSE use `sudo zypper install ./st-*.rpm`.)

#### Launch CubeIDE

```bash
/opt/st/stm32cubeide_x.y.z/stm32cubeide
```

Adjust the path if you chose a different location. Create a launcher/desktop shortcut if one was not added. On first start, select a workspace folder (e.g. `~/stm32_ws`).

### 3.3 Install STM32CubeProgrammer

```bash
cd ~/Downloads
unzip en.stm32cubeprg-lin_v*.zip -d stm32cubeprog-installer
cd stm32cubeprog-installer
chmod +x SetupSTM32CubeProgrammer-*.linux
./SetupSTM32CubeProgrammer-*.linux
```

The graphical installer guides you through the process. Choose an install directory, for example:

- **User install:** `~/STMicroelectronics/STM32Cube/STM32CubeProgrammer`
- **System-wide:** `/usr/local/STMicroelectronics/STM32Cube/STM32CubeProgrammer` (run the installer with `sudo`)

> The Linux zip may also contain a Windows `.exe`; ignore it.

#### Add the CLI to your PATH

```bash
# Adjust the path to match where you installed it
echo 'export PATH=$HOME/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

Or create a symlink (system-wide install):

```bash
sudo ln -s /usr/local/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI /usr/local/bin/STM32_Programmer_CLI
```

### 3.4 Install udev rules (required for USB access)

Without these rules, ST-LINK, J-Link and USB DFU devices only work as root. Copy the rules shipped with CubeProgrammer and reload:

```bash
cd ~/STMicroelectronics/STM32Cube/STM32CubeProgrammer/Drivers/rules
sudo cp *.* /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Unplug and re-plug your board afterwards.

(If you used the CubeIDE `.sh`, `.deb` or `.rpm` installer, it normally installs ST-LINK udev rules too. Copying the CubeProgrammer rules is still recommended for DFU support.)

### 3.5 Serial/UART bootloader access (optional)

If you flash over UART (e.g. `/dev/ttyACM0` or `/dev/ttyUSB0`), add your user to the `dialout` group, then log out and back in:

```bash
sudo usermod -aG dialout $USER
```

### 3.6 Verify on Linux

Plug in your board, then:

```bash
STM32_Programmer_CLI -l          # list connected probes
STM32_Programmer_CLI -c port=SWD # connect over SWD
```

Launch the GUI with:

```bash
~/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32CubeProgrammer
```

In CubeIDE, create a new STM32 project, build it, and start a debug session to confirm that the ST-LINK GDB server connects.

### 3.7 Linux troubleshooting

| Problem | Fix |
|---|---|
| `No STLink detected` / permission denied | Confirm the udev rules are in `/etc/udev/rules.d/`, reload them, and re-plug the board. Check `lsusb` shows the device. |
| Debugger fails with `libncurses.so.5` or `libtinfo.so.5` missing | Install the compatibility library for your distro (e.g. `libncurses5` / `ncurses-compat-libs`). Newer distros may need it from a compatibility repository. |
| GUI won't start / Qt or XCB errors | Install common GUI libraries, e.g. `sudo apt install libgl1 libxcb-xinerama0 libxkbcommon-x11-0`. |
| Installer refuses to run | Make sure it is executable (`chmod +x`) and that you downloaded the Linux package (not the Windows one). |
| CubeProgrammer icon missing (Ubuntu) | Launch from the `bin` folder or create a `.desktop` entry manually. |
| USB DFU inside Docker | Install udev rules on the **host**, then start the container with `--privileged` or appropriate `--device` flags and `--net=host`. |

---

## 4. Post-install checklist

- [ ] STM32CubeIDE opens and creates/builds a project
- [ ] Board is detected by STM32CubeProgrammer (ST-LINK → Connect)
- [ ] ST-LINK firmware is up to date
- [ ] Debug session starts in CubeIDE
- [ ] (Optional) STM32CubeMX installed separately
- [ ] (Optional) CLI on PATH: `STM32_Programmer_CLI --help`

### Quick flash test with the CLI

```bash
# Flash a .bin at the start of flash (0x08000000), verify, then reset
STM32_Programmer_CLI -c port=SWD -w firmware.bin 0x08000000 -v -rst

# Flash an .elf or .hex (address is embedded in the file)
STM32_Programmer_CLI -c port=SWD -w firmware.elf -v -rst
```

---

## 5. Updating and uninstalling

**Updating**
- **CubeIDE:** *Help → Check for Updates*, or install the newer version side by side (each release uses its own folder). Existing projects may need to be imported into the new version.
- **CubeProgrammer:** use the built-in updater, or download and run the newer installer.

**Uninstalling**
- **Windows:** Settings → Apps → Installed apps → uninstall each tool.
- **Linux:** run the `Uninstall` executable in each install folder, or `sudo apt remove <package>` / `sudo dnf remove <package>` for DEB/RPM installs. Remove old rules from `/etc/udev/rules.d/` if desired.

---

## 6. Official references

- STM32CubeIDE installation guide **UM2563**, quick start guide **UM2553**, user guide **UM2609**
- STM32CubeIDE page: <https://www.st.com/en/development-tools/stm32cubeide.html>
- STM32CubeProgrammer page: <https://www.st.com/en/development-tools/stm32cubeprog.html>
- STM32CubeProgrammer docs: <https://dev.st.com/stm32cube-docs/stm32cubeprogrammer>
- ST Community forum: <https://community.st.com>