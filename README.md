# arctic-monitor

System for monitoring an ArcGIS concurrent license manager

This is a small Dockerized app written in Python running as a service.
The Python script needs to query the license manager and it does that
using the "lmutil" command line utility that is included in the
Esri download for the license manager.

Because the license manager "Flexera FlexLM" is licensed software, if
you want to use this monitor in the Docker, you will need to download
the Linux version of the license manager package from ESRI and put it
here in the project folder before doing the Docker build.

## The obligatory screenshot

It does not look like this right now, I am redoing the HTML page.

![Screenshot of monitor for ArcGIS Flexlm](screenshot.png?raw=true "What the web page looks like")

### Prerequisites

The Dockerfile is based on this version of the license manager:
ArcGIS_License_Manager_Linux_2021.0_177950.tar.gz

I don't think it matters very much which version you use, because it is
just interrogating the real license server over a network connection.
But when the version number changes you can change the Dockerfile.

To get the tar file, go to my.esri.com and download the latest Linux
license manager.  It will be a file ending in 'tar.gz'. Put the file
in this folder. (The one containing the Dockerfiles.)

### Notes on the Dockerfile

The requirements doc at ESRI call for RHEL 6 or 7;
this Dockerfile uses Centos 7 and Debian 11.

I took the list of required RPM packages from the ESRI documentation and
dropped them into the Dockerfile as "stage1".

I broke up the package installation into multiple RUN commands. That's
because when I tried doing them in one pass, it failed. I did not try
to fine tune it or confirm which ones were really needed or what order
to install them in once I got it working.

The license manager installation step is done in "silent" mode so
there is no requirement for any X Window server or any interactions
from you.

I don't like Redhat, so stage 2 of the Dockerfile uses Debian 11.
The final image is smaller. I am sure it could go a lot smaller but
I am done for today.

### Docker build

Because of the licensing constraints I don't push this image up to Docker Hub.

Make sure you've downloaded the tar.gz file, see Prerequisites.

Then run the build command to create images for the license manager and the monitor.

**Install service.txt** -- In the interest of simplicity you 
have to put a copy of your service.txt file
from your license server here so that it can be baked into the build. I could
have used a bind mount or a volume but this is easy and you have to build 
your own image anyway due to aforementioned license requirements.

```bash
docker build -t wildsong/arctic-monitor .
```

If the build fails with a message about not being able to ADD then you
did not put the tar.gz file here or you need to update its name in
"Dockerfile.flexlm" around line 51.

After the license manager is installed Docker will emit a long series
of Copy File and Install File messages from the flexlm installer. It
will stop at this point if the install fails.

For the monitor, only file we need from the ESRI installation is lmutil.
When the stage 2 image is built, the file will be copied from the stage1 image to the stage 2.

Once the builds complete you will have an image 
called "wildsong/arctic-monitor" with the lmutil tool 
and the python web server.

### Confirm the build (optional step!)

You can look around in the new container by launching into a bash shell.
If you don't want to, skip to the next section.

```bash
    docker run -it --rm wildsong/arctic-monitor bash
```

When you are in the shell you can run "./test.sh" and it should dump
out the license info. You can run "python read_lmutil.py" to make sure
it can run the Python as well.

## Deployment

The python code and its environment were already set up in the Docker
file.

If you are only running the monitor container then you need a current
copy of the "service.txt" file from your license manager.  You need to
edit the service.txt file so that it has the actual license server
host name instead of "This_Host".  Copy the service.txt file into the
config/ directory, and edit it.

When using both containers the name of the lmgrd host and the name in the service.txt
file have to match. When running the lmgrd somewhere else it has to be
the name of that other machine.

Now you just have to run the containers.

```bash
docker-compose up -d
```

If you only want to run the monitor, you should be able to type

```bash
    docker-compose up monitor
```

The monitor will show up at <http://localhost:5000/> (or use your server
name in place of localhost if you are not running it locally).

The output of my running license manager looked like this when I started it.

```bash
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) ===============================================
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) === Vendor Daemon ===
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Vendor daemon: ARCGIS
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Start-Date: Fri Feb 26 2021 14:23:57 PST
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) PID: 8
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) VD Version: v11.16.5.1 build 257031 x64_lsb ( build 257031 (ipv6))
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@)
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) === Startup/Restart Info ===
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Options file used: None
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Is vendor daemon a CVD: No
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Is FlexNet Licensing Service installed and compatible: No
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) FlexNet Licensing Service Version: -NA-
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Is TS accessed: No
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) TS access time: -NA-
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Number of VD restarts since LS startup: 0
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@)
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) === Network Info ===
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Listening port: 27001
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Daemon select timeout (in seconds): 1
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@)
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) === Host Info ===
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Host used in license file: cc-testmaps
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) HostID node-locked in license file: NA
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) HostID of the License Server: 0242ac150003
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) Running on Hypervisor: Unknown Hypervisor
lmgrd_1    | 14:23:57 (ARCGIS) (@ARCGIS-SLOG@) ===============================================
lmgrd_1    | 14:24:33 (ARCGIS) TCP_NODELAY NOT enabled
```

## Misc

I previously started working on a Windows-based monitor and quit when
I found out how hard it was (FOR ME) to work with Docker On Windows.

That incomplete repo is still out there. See
<http://github.com/brian32768/node-service>

### Another similar project

Uses lmutil and stores output in SQL Server:
<https://github.com/jmitz/ArcGISLicenseMonitor/blob/master/LicenseMonitor.py>

### WATCHING THE LOG FILE

14:46:39 (telelogic) DENIED: DOORS indkach@indkach  [telelogic]
(Licensed number of users already reached. (-4,342:10054 ))
14:46:39 (telelogic) DENIED: DOORS indkach@indkach  [telelogic]
(Licensed number of users already reached. (-4,342:10054 ))
14:46:39 (telelogic) OUT: TLSTOK-token indkach@indkach  [DOORS]
(3 licenses)

### REPORT LOGGING - can be enabled in OPTIONS file but produces an encrypted file that is of no use without Flexera software

See <https://openlm.com/blog/are-flexnet-flexlm-manager-report-logs-essential-for-license-consumption-monitoring/>

### Version 2 ideas

The advantage of doing this is that I can see the log file and respond as soon as anything happens instead of polling. 
The disadvantage is that if the server is down, the monitoring web site will be down too. Further it precludes multiple redundant license servers.

If I put a microservice on the actual license manager, and let it run both lmstat
and monitor the logs, and then make a dumber flask app that does not need to have
lmstat installed, I will be several steps ahead. So I will be doing that on the "dev"
branch of this project starting right this minute.

The microservice would be a MQTT publisher instead of running over HTTP,
the pub/sub model makes more sense here.
