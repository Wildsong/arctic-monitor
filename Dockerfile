FROM centos:7 as stage1

# =================================================================
# STAGE 1 -- Configure a build host and install the license manager
# This list of packages is from the ESRI requirements description.
# It includes the entire X-Window server that we will never need.
# Hence the multistage build, first download many files so that
# the Esri installer can run in silent mode, and then 
# ignore them in stage2.

RUN yum install -y \
 compat-libstdc++-33.i686 \
 compat-libf2c-34.i686 \
 compat-openldap.i686 \
 cairo.i686 \
 freeglut.i686 \
 fuse-libs.i686 \
 gmp.i686 \
 gtk2.i686 \
 PackageKit-glib.i686 \
 PackageKit-gtk3-module.i686 \
 polkit.i686 \
 polkit.x86_64 \
 redhat-lsb.i686

RUN yum install -y \
 libcanberra.i686 \
 libgcc.i686 \
 libgfortran.i686 \
 libidn.i686 \
 libstdc++.i686 \
 libSM.i686 \
 libX11.i686 \
 libXau.i686 \
 libxcb.i686 \
 libXdamage.i686 \
 libXext.i686 \
 libXfixes.i686 \
 libXrender.i686 \
 libXp.i686 \
 libXScrnSaver.i686 \
 libXtst.i686

RUN yum install -y \
 mesa-libGL.i686 \
 mesa-libGLU.i686

RUN adduser flexlm && \
    mkdir -p /usr/local/share/macrovision/storage && \
    chmod 777 /usr/local/share/macrovision/storage

USER flexlm
WORKDIR /home/flexlm

COPY ArcGIS_License_Manager_Linux_2022_1_184756.tar.gz LicenseManager.tar.gz
RUN tar xzvf LicenseManager.tar.gz && \
    cd LicenseManager_Linux && \
    ./Setup -l Yes -m silent

# Dump messages out so that errors will be visible on the console when building 
RUN cat arcgis/licensemanager/.Setup/LicenseManager_InstallLog.log

USER root

# ===========================================
# STAGE 2 -- install and run the microservice
# The conda/miniconda3 image is based on Debian Stretch
FROM conda/miniconda3
ADD https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh .
RUN sh Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda
ENV PATH=/opt/conda/bin:${PATH}
RUN apt-get update && apt-get install -y curl gnupg

# This will upgrade conda, so the fact that the base image is old does not matter
# flask-bootstrap needs hugo
RUN conda update -n base -c defaults conda
RUN conda config --add channels conda-forge && \
    conda config --add channels hugo && \
    conda config --add channels Esri
COPY conda_requirements.txt ./
RUN conda install --file conda_requirements.txt

# Add the ODBC driver so we can talk to SQL Server
# Use the DEBIAN 9 install instructions.
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN adduser flexlm
WORKDIR /home/flexlm
COPY --from=stage1 /home/flexlm/arcgis/licensemanager/bin/lmutil .

#RUN cd /lib/lib/x86_64-linux-gnu && \
    

ENV LMHOME /home/flexlm
ENV LMUTIL /home/flexlm/lmutil
ENV LICENSE /home/flexlm/service.txt

USER flexlm

# Install the microservice
COPY license_monitor.py .
COPY read_lmutil.py .
COPY read_sqlserver.py .
COPY config.py .
COPY test.sh .
COPY start_server.py .

#VOLUME /home/flexlm/service.txt
COPY service.txt .

EXPOSE 5000

# Run the microservice
CMD ["python3", "start_server.py"]
