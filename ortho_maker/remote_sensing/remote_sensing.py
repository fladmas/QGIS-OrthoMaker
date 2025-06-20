# -*- coding: utf-8 -*-
#-----------------------------------------------------------
#
# RemoteSensing Library
# Copyright (C) 2015 Flatman, Falkenberg - Danish National Mapping Agengy
# EMAIL: anfla (at) sdfe.sk
# WEB  : http://www.sdfe.dk
#
# A simple tool for checking images for radiometry and geometry
# Version 1
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

import math
import psycopg2
from datetime import datetime


def ray(IO, EO, Z, col,row):
    # def ray(xx0,yy0,c,pix,dimX,dimY,X0,Y0,Z0,Ome,Phi,Kap,Z,col,row):
    xx0 = IO[0]
    yy0 = IO[1]
    c = IO[2]
    pix = IO[3]
    dimX = IO[4]
    dimY = IO[5]
    X0 = EO[0]
    Y0 = EO[1]
    Z0 = EO[2]
    Ome = EO[3]
    Phi = EO[4]
    Kap = EO[5]
    o = math.radians(Ome)
    p = math.radians(Phi)
    k = math.radians(Kap)
    D11 =   math.cos(p) * math.cos(k)
    D12 = - math.cos(p) * math.sin(k)
    D13 =   math.sin(p)
    D21 =   math.cos(o) * math.sin(k) + math.sin(o) * math.sin(p) * math.cos(k)
    D22 =   math.cos(o) * math.cos(k) - math.sin(o) * math.sin(p) * math.sin(k)
    D23 = - math.sin(o) * math.cos(p)
    D31 =   math.sin(o) * math.sin(k) - math.cos(o) * math.sin(p) * math.cos(k)
    D32 =   math.sin(o) * math.cos(k) + math.cos(o) * math.sin(p) * math.sin(k)
    D33 =   math.cos(o) * math.cos(p)

    x_dot = ((col-(dimX/2))*pix)+xx0
    y_dot = ((row-(dimY/2))*pix)+yy0

    x_dot = ((col*pix)-dimX*-1)-xx0
    y_dot = ((row*pix)-dimY*-1)-yy0

    kx=(D11*x_dot + D12*y_dot + D13*c)/(D31*x_dot + D32*y_dot + D33*c)
    ky=(D21*x_dot + D22*y_dot + D23*c)/(D31*x_dot + D32*y_dot + D33*c)

    X=(Z-Z0)*kx + X0
    Y=(Z-Z0)*ky + Y0
    #newZ=(Y-Y0)/ky + Z0
    #print newZ


    return(X,Y)

def rayverse(IO, EO, X, Y, Z):
    # def ray(xx0,yy0,c,pix,dimX,dimY,X0,Y0,Z0,Ome,Phi,Kap,Z,col,row):
    xx0 = IO[0]
    yy0 = IO[1]
    c = IO[2]
    pix = IO[3]
    dimX = IO[4]
    dimY = IO[5]
    X0 = EO[0]
    Y0 = EO[1]
    Z0 = EO[2]
    Ome = EO[3]
    Phi = EO[4]
    Kap = EO[5]
    o = math.radians(Ome)
    p = math.radians(Phi)
    k = math.radians(Kap)
    D11 =   math.cos(p) * math.cos(k)
    D12 = - math.cos(p) * math.sin(k)
    D13 =   math.sin(p)
    D21 =   math.cos(o) * math.sin(k) + math.sin(o) * math.sin(p) * math.cos(k)
    D22 =   math.cos(o) * math.cos(k) - math.sin(o) * math.sin(p) * math.sin(k)
    D23 = - math.sin(o) * math.cos(p)
    D31 =   math.sin(o) * math.sin(k) - math.cos(o) * math.sin(p) * math.cos(k)
    D32 =   math.sin(o) * math.cos(k) + math.cos(o) * math.sin(p) * math.sin(k)
    D33 =   math.cos(o) * math.cos(p)

    x_dot = (-1)*c*((D11*(X-X0)+D21*(Y-Y0)+D31*(Z-Z0))/(D13*(X-X0)+D23*(Y-Y0)+D33*(Z-Z0)))
    y_dot = (-1)*c*((D12*(X-X0)+D22*(Y-Y0)+D32*(Z-Z0))/(D13*(X-X0)+D23*(Y-Y0)+D33*(Z-Z0)))

    col = ((x_dot-xx0)+(dimX))*(-1)/pix
    row = ((y_dot-yy0)+(dimY))*(-1)/pix

    return(col,row)

def CreateSURE(OutPath, IMGpath, IO, EO):
    PriX = IO[0]
    #print 'PriX'+str(PriX)
    PriY = IO[1]
    CC = IO[2] * (-1)
    pix = IO[3]
    #print 'pix'+str(pix)
    SensorX = int(IO[4]*-2/pix)
    SensorY = int(IO[5]*-2/pix)
    X = EO[0]
    Y = EO[1]
    Z = EO[2]
    Omega = EO[3]
    Phi = EO[4]
    Kappa = EO[5]

    PriXpix = (SensorX / 2) + ((PriX / pix))
    PriYpix = (SensorY / 2) + ((PriY / pix))

    r = math.pi / 180
    #print r

    SO = math.sin(Omega * r);
    CO = math.cos(Omega * r);
    SP = math.sin(Phi * r);
    CP = math.cos(Phi * r);
    CK = math.cos(Kappa * r);
    SK = math.sin(Kappa * r);
    rot0 = CP * CK;
    rot1 = CO * SK + SO * SP * CK;
    rot2 = SO * SK - CO * SP * CK;
    rot3 = CP * SK;
    rot4 = -CO * CK + SO * SP * SK;
    rot5 = -SO * CK - CO * SP * SK;
    rot6 = -SP;
    rot7 = SO * CP;
    rot8 = -CO * CP;

    CCpix = CC / pix

    with open(OutPath, "w") as text_file:
        text_file.write("$ImageID___________________________________________________(ORI_Ver_1.0)" + " \n")
        text_file.write("\t" + IMGpath + " \n")
        text_file.write("$IntOri_FocalLength_________________________________________________[mm]" + " \n")
        text_file.write("\t" + str(CC) + " \n")
        text_file.write("$IntOri_PixelSize______(x|y)________________________________________[mm]" + " \n")
        text_file.write("\t" + str(pix) + "\t " + str(pix) + " \n")
        text_file.write("$IntOri_SensorSize_____(x|y)_____________________________________[pixel]" + " \n")
        text_file.write("\t" + str(SensorX) + "\t " + str(SensorY) + " \n")
        text_file.write("$IntOri_PrincipalPoint_(x|y)_____________________________________[pixel]" + " \n")
        text_file.write("\t" + str(PriXpix) + "\t " + str(PriYpix) + " \n")
        text_file.write("$IntOri_CameraMatrix_____________________________(ImageCoordinateSystem)" + " \n")
        text_file.write("\t" + str(CCpix) + "\t " + "0.00000000" + "\t " + str(PriXpix) + " \n")
        text_file.write("\t" + "0.00000000" + "\t " + str(CCpix) + "\t " + str(PriYpix) + " \n")
        text_file.write("\t" + "0.00000000" + "\t" + " 0.00000000" + "\t" + " 1.00000000" + " \n")
        text_file.write("$ExtOri_RotationMatrix____________________(World->ImageCoordinateSystem)" + " \n")
        text_file.write("\t" + str(rot0) + "\t " + str(rot1) + "\t " + str(rot2) + " \n")
        text_file.write("\t" + str(rot3) + "\t " + str(rot4) + "\t " + str(rot5) + " \n")
        text_file.write("\t" + str(rot6) + "\t " + str(rot7) + "\t " + str(rot8) + " \n")
        text_file.write("$ExtOri_TranslationVector________________________(WorldCoordinateSystem)" + " \n")
        text_file.write("\t" + str(X) + "\t " + str(Y) + "\t " + str(Z) + " \n")
        text_file.write("$IntOri_Distortion_____(Model|ParameterCount|(Parameters))______________" + " \n")
        text_file.write("\t" + "none 0")
        text_file.close()

def CreateFootprint(IO, EO):
    # def CreateFootprint(xx0, yy0, c, pix, dimX, dimY, X0, Y0, Z0, Ome, Phi, Kap):
    xx0 = IO[0]
    yy0 = IO[1]
    c = IO[2]
    pix = IO[3]
    dimX = IO[4]
    dimY = IO[5]
    X0 = EO[0]
    Y0 = EO[1]
    Z0 = EO[2]
    Ome = EO[3]
    Phi = EO[4]
    Kap = EO[5]

    xy1 = ray(IO, EO, 0, 0, 0)
    xy2 = ray(IO, EO, 0, dimX*-2/pix, 0)
    xy3 = ray(IO, EO, 0, dimX*-2/pix, dimY*-2/pix)
    xy4 = ray(IO, EO, 0, 0, dimY*-2/pix)

    Poly = [(xy1[0],xy1[1]),(xy2[0],xy2[1]),(xy3[0],xy3[1]),(xy4[0],xy4[1])]

    return(xy1, xy2, xy3, xy4, Poly)

def uploadCAM(camfile):

    return

def createDef(defName, IMGpath, DEMpath, ORTpath, IO, EO, Poly, RES, TYP):


    xx0 = IO[0]
    yy0 = IO[1]
    c = IO[2]
    pix = IO[3]
    dimX = IO[4]
    dimY = IO[5]
    X0 = EO[0]
    Y0 = EO[1]
    Z0 = EO[2]
    Ome = EO[3]
    Phi = EO[4]
    Kap = EO[5]


    # *** Calculate Orto Extents ***
    bbox = BoundingBox(Poly)
    TLX = int(round((bbox[0] / float(RES)), 0) * float(RES))
    TLY = int(round((bbox[3] / float(RES)), 0) * float(RES))
    LRX = int(round((bbox[1] / float(RES)), 0) * float(RES))
    LRY = int(round((bbox[2] / float(RES)), 0) * float(RES))
    OSizeX = (LRX - TLX)
    OSizeY = (TLY - LRY)
    SZX = (LRX - TLX) / float(RES)
    SZY = (TLY - LRY) / float(RES)

    # *** adjust for camera rotation ***
    if IO[6] == 0:
        IL1 = "0.000 " + str(IO[3])
        IL2 = str(IO[3]) + " 0.000 "
        IL3 = str(IO[4]) + " " + str(IO[5])
        PriY = str(IO[0])
        PriX = str(IO[1])

    elif IO[6] == 180:
        IL1 = " 0.000 " + str(IO[3])
        IL2 = str(IO[3]) + " 0.000 "
        IL3 = str(IO[5]) + " " + str(IO[4] * (-1))
        PriY = str(IO[0])
        PriX = str(IO[1])

    elif IO[6] == 90:
        IL1 = str(IO[3]) + " 0.000"
        IL2 = "0.000 " + str(IO[3] * (-1))
        IL3 = str(IO[5]) + " " + str(IO[4]*(-1))
        PriY = str(IO[1])
        PriX = str(IO[0])

    elif IO[6] == 270:
        IL1 = str(IO[3]) + " 0.000"
        IL2 = "0.000 " + str(IO[3] * (-1))
        IL3 = str(IO[4]) + " " + str(IO[5]*(-1))
        PriY = str(IO[1])
        PriX = str(IO[0])

    elif IO[6] == 999:
        IL1 = str(IO[3]) + " 0.000"
        IL2 = "0.000 " + str(IO[3] * (-1))
        IL3 = str(IO[5]*(-1)) + " " + str(IO[4])
        PriY = str(IO[1])
        PriX = str(IO[0])
    else:
        print ("Illegal Camera Rotation" + str(IO[6]))
        exit()

    # IL1 = "0.000 " + str(IO[3])
    # IL2 = str(IO[3]) + " 0.000 "
    # IL3 = str(IO[4]) + " " + str(IO[5])
    # PriY = str(IO[0])
    # PriX = str(IO[1])

    # *** write DEF file ***
    with open(defName, "w") as text_file:
        text_file.write("PRJ= nill.apr" + " \n")
        text_file.write("ORI= nill.txt" + " \n")
        text_file.write("RUN= 0" + " \n")
        text_file.write("DEL= NO" + " \n")
        text_file.write("IMG= " + IMGpath + " \n")
        text_file.write("DTM= " + DEMpath + " \n")
        text_file.write("ORT= " + ORTpath + " \n")
        text_file.write("TLX= " + str(TLX) + " \n")
        text_file.write("TLY= " + str(TLY) + " \n")
        text_file.write("OPM= " + TYP + " \n")
        text_file.write("RES= " + str(RES) + " \n")
        text_file.write("SZX= " + str(math.trunc(SZX)) + " \n")
        text_file.write("SZY= " + str(math.trunc(SZY)) + " \n")
        text_file.write("R34= NO" + " \n")
        text_file.write("INT= CUB -1" + " \n")
        text_file.write("CON= " + str(IO[2] / 1000) + " \n")  # 0.1005
        text_file.write("XDH= " + PriX + " \n")  #str(IO[0]) + " \n")  # -0.18
        text_file.write("YDH= " + PriY + " \n")  #str(IO[1]) + " \n")
        text_file.write("IL1= " + IL1 + " \n")   #str(IO[3]) + " 0.000 \n")
        text_file.write("IL2= " + IL2 + " \n")   #"0.000 " + str(IO[3] * (-1)) + " \n")
        text_file.write("IL3= " + IL3 + " \n")   #str(IO[4]*-IO[3]/2) + " " + str(IO[5]*IO[3]/2) + " \n")
        text_file.write("X_0= " + str(EO[0]) + " \n")
        text_file.write("Y_0= " + str(EO[1]) + " \n")
        text_file.write("Z_0= " + str(EO[2]) + " \n")
        text_file.write("DRG= DEG" + " \n")
        text_file.write("OME= " + str(EO[3]) + " \n")
        text_file.write("PHI= " + str(EO[4]) + " \n")
        text_file.write("KAP= " + str(EO[5]) + " \n")
        text_file.write("MBF= 870" + " \n")
        text_file.write("BBF= 999999" + " \n")
        text_file.write("STR= NO" + " \n")

        # if typen == "polygon" and self.dlg.checkBox_bbox.isChecked():
        #     for punktliste in Geometri:
        #         text_file.write("BPL= " + str(len(punktliste)) + " 0" + " \n")
        #         punktnummer = 0
        #         for punkt in punktliste:
        #             punktnummer = punktnummer + 1
        #             text_file.write("BP" + str(punktnummer) + "=" + str(punkt.x()) + " " + str(punkt.y()) + " \n")

        text_file.close()

    return

def getIO(cameraID,coneID,date):

    schem = 'remote_sensing'
    tabl = 'camera_calibrations'
    if coneID == '' or coneID =='None':
        coneID = '0'

    conn = psycopg2.connect(
        "dbname={name} user={user} host={host} password={pswd} port={port}".format(
            name='postgres',#geo',
            user='python_script_sdfe',#geo_rs_user',
            schem='remote_sensing',
            tabl='camera_calibrations',
            host='C1507145',#loaddb14.kmsext.dk',
            pswd='python_script_sdfe',#geo_rs_user',
            port='5432',#11414',
        )
    )

    cur = conn.cursor()

    dbkald = "SELECT * FROM " + schem + "." + tabl + " WHERE camera_id = \'" + str(cameraID) + "\' and cone_id = \'" + coneID + "\' and calibration_date < \'" + date + "\' order by calibration_date DESC limit 1"

    print (dbkald)

    cur.execute(dbkald)
    ccdb_svar = cur.fetchone()

    try:
        imgRot = ccdb_svar[14]
        CamRot = ccdb_svar[13]
        c = float(ccdb_svar[1]) * (-1)  # 100.5
        pix = ccdb_svar[2] / 1000  # 0.006
        #dimX = int(ccdb_svar[5]*-2/pix)  # 11310
        #dimY = int(ccdb_svar[6]*-2/pix)  # 17310
        dimXi = float(ccdb_svar[5])  # -34.008
        dimYi = float(ccdb_svar[6])  # -52.026
        xx0i = float(ccdb_svar[3])  # (-18)
        yy0i = float(ccdb_svar[4])  # (0)
        coneid = ccdb_svar[15]

        #*** Rotate da shit ***
        if CamRot == 0:
            dimX = dimXi
            dimY = dimYi
            xx0 = xx0i
            yy0 = yy0i
        if CamRot == 90:
            dimX = dimXi
            dimY = dimYi
            xx0 = xx0i
            yy0 = yy0i
        if CamRot == 180:
            dimX = dimXi
            dimY = dimYi
            xx0 = xx0i
            yy0 = yy0i
        if CamRot == 270:
            dimX = dimXi
            dimY = dimYi
            xx0 = xx0i
            yy0 = yy0i


    except (RuntimeError, TypeError, NameError, ValueError):
        noError = False
        print ('error')

    IO = [xx0,yy0,c,pix,dimX,dimY,CamRot]
    return(IO)

def BoundingBox(poly):
    minx, miny = float("inf"), float("inf")
    maxx, maxy = float("-inf"), float("-inf")
    for x, y in poly:
        # Set min coords
        if x < minx:
            minx = x
        if y < miny:
            miny = y
        # Set max coords
        if x > maxx:
            maxx = x
        if y > maxy:
            maxy = y
    bbox = [minx, maxx, miny, maxy]
    return (bbox)

def setDB():
    global db_name
    global db_name
    global db_host
    global db_port
    global db_user
    global db_pass
    global db_schema
    global db_table
    global db_geom

    # C1200038
    db_name = "postgres"
    db_host = "C1507145"
    db_port = "5432"
    db_user = "rs_user"
    db_pass = "rs_user"

    # Herunder opsaettes tabellen der skal bruges
    db_schema = "gru"
    db_table = 'jobque'
    db_geom = "geom"

    conn = psycopg2.connect(
        "dbname={name} user={user} host={host} password={pswd}".format(
            name=db_name,
            user=db_user,
            host=db_host,
            pswd=db_pass,
        )
    )
    return conn

def MinionManager(job_type,path_bat_file,created_by,wkt):
    conn = setDB()
    cur = conn.cursor()

    job_id = 4
    #job_type = 'SURE'
    job_status = 'Pending'
    minion_id = ''
    start_time = 'null'
    end_time = 'null'
    progress = 0
    #path_bat_file = defPath
    priority = 1
    creation_time = str(datetime.now())
    #created_by = ''
    comment = ''
    #geometri = "ST_GeomFromText('"+wkt.asWkt()+"',25832)"
    try:
        geometri = 'ST_GeomFromText(\''+wkt+'\',25832)'
    except:
        geometri = "ST_GeomFromText('" + wkt.asWkt() + "',25832)"
    #geometri = 'ST_GeomFromText('MULTIPOLYGON (((871120 6138505, 871988 6138505, 871988 6136242, 871120 6136242, 871120 6138505)))', 25832)'



    dbkald = "INSERT INTO "+ db_schema +"."+ db_table +"(job_type,job_status,progress,path_bat_file,priority,creation_time,created_by,geom) VALUES(\'"+ job_type + "','" + job_status + "','" + str(progress) + "','" + path_bat_file + "'," + str(priority) + ",'" + creation_time + "','" + created_by + "'," + geometri +");"
    #dbkald = "UPDATE " + db_schema + "." + db_table + " SET path = \'" + str(newline) + "\' WHERE imageid = \'" + str(imageName2) + "\'"
    print (dbkald)
    cur.execute(dbkald)

    conn.commit()

def GRUorto(schem,tabl):
    conn = setDB()
    cur = conn.cursor()
    try:
        cur = conn.cursor()
        #dbkald = "SELECT * FROM " + schem + "." + tabl + " WHERE qo_done = 'New' and level > 1 and size_kb_tif > 10 order by time_file_tif limit 1"
        dbkald = "SELECT imageid," \
                 "easting," \
                 "northing," \
                 "height," \
                 "omega," \
                 "phi," \
                 "kappa," \
                 "timeutc," \
                 "cameraid," \
                 "coneid," \
                 "image_path_tif," \
                 "geom," \
                 "gsd" \
                 " FROM " + schem + "." + tabl + " WHERE qo_done = 'New' and comment_co != 'crossstrip' and level > 1 and size_kb_tif > 10 order by time_file_tif limit 1"
                 #" FROM " + schem + "." + tabl + " WHERE qo_done = 'New' and direction = 'T' and level > 1 and size_kb_tif > 10 order by time_file_tif limit 1"
        cur.execute(dbkald)
        if cur.rowcount == 0:
            #print ('No new orthos, will now fool around for a minute - ' + str(datetime.now()))
            return -1, 'NoNew'
        else:
            ccdb_svar = cur.fetchone()
            print (ccdb_svar)
            #myorder = [2, ]
            ImageID = str(ccdb_svar[0])
            print ('id: ' + ImageID)

            try:
                gsd = float(ccdb_svar[12])
            except:
                gsd = 0.1

            if (gsd>0.12):
                RES = "0.16"
                finalDst = '\\\\kmsload157.kmsext.dk\\data\\mapserver\\data\\ortofoto\\2019_quickorto\\16cm\\'
            else:
                RES = "0.1"
                finalDst = '\\\\kmsload157.kmsext.dk\\data\\mapserver\\data\\ortofoto\\2019_quickorto\\10cm\\'
            #finalDst = 'F:\\JOB\\DATA\\RemoteSensing\\Drift\\GRU\\orto_output\\'


            basepath = 'F:\\JOB\\DATA\\RemoteSensing\\Drift\\GRU\\orto_bat_files\\'
            calcPath = 'C:\\temp\\COWStemp\\'
            jpegPath = calcPath + 'jpeg\\'




            OName = "O" + ImageID + ".tif"
            ortName = calcPath + OName
            DEMpath = calcPath + "DTM_" + ImageID + ".asc"

            filnavn = ImageID
            orto_batfil = basepath + filnavn + '.bat'
            defName = basepath + filnavn + '.def'
            Z = 0

            cameraID = str(ccdb_svar[8])
            imageDate = str(ccdb_svar[7])
            imgpath = str(ccdb_svar[10])
            coneID = str(ccdb_svar[9])
            IO = getIO(cameraID, coneID, imageDate)
            pix = IO[3]
            dimX = IO[4] * -2 / pix
            dimY = IO[5] * -2 / pix
            print(IO)

            filnavn = ImageID
            X0 = (ccdb_svar[1])
            Y0 = (ccdb_svar[2])
            Z0 = (ccdb_svar[3])
            Ome = (ccdb_svar[4])
            Phi = (ccdb_svar[5])
            Kap = (ccdb_svar[6])


            EO = [X0, Y0, Z0, Ome, Phi, Kap]
            print(EO)

            with open(orto_batfil, "w") as bat_file:
                #defnr = defnr + 1

                # ***  processingmanager info ***
                jobnavn = ImageID[5:10]
                bat_file.write('python C:/temp/writeProgress.py ' + jobnavn + " 50 \n")

                if (dimX < dimY):
                    UL = ray(IO, EO, Z, dimX * 0.25, dimY * 0.07)
                    UR = ray(IO, EO, Z, dimX * 0.25, dimY * 0.93)
                    LR = ray(IO, EO, Z, dimX * 0.75, dimY * 0.93)
                    LL = ray(IO, EO, Z, dimX * 0.75, dimY * 0.07)
                else:
                    UL = ray(IO, EO, Z, dimX * 0.07, dimY * 0.25)
                    UR = ray(IO, EO, Z, dimX * 0.07, dimY * 0.75)
                    LR = ray(IO, EO, Z, dimX * 0.93, dimY * 0.75)
                    LL = ray(IO, EO, Z, dimX * 0.93, dimY * 0.25)

                Polyg = [(UL[0], UL[1]), (UR[0], UR[1]), (LR[0], LR[1]), (LL[0], LL[1])]

                bbox = BoundingBox(Polyg)
                TLX = int(round((bbox[0] / float(RES)), 0) * float(RES))
                TLY = int(round((bbox[3] / float(RES)), 0) * float(RES))
                LRX = int(round((bbox[1] / float(RES)), 0) * float(RES))
                LRY = int(round((bbox[2] / float(RES)), 0) * float(RES))
                BoBox = 'MULTIPOLYGON (((' + str(TLX) + ' ' + str(TLY) + ', ' + str(LRX) + ' ' + str(TLY) + ', ' + str(LRX) + ' ' + str(LRY) + ', ' + str(TLX) + ' ' + str(LRY) + ', ' + str(TLX) + ' ' + str(TLY) + ')))'
                bat_file.write("cd c:\\temp \n")
                # bat_file.write("net use P: /delete\n")
                # bat_file.write("net use P: \\\\10.48.196.223\\Peta_Lager_3 rs@1809GEOD /user:PROD\\b025527 /persistent:yes\n")
                # bat_file.write("net use X: /delete\n")
                # bat_file.write("net use X: \\\\10.48.195.15\\Data_4 rs@1809GEOD /user:PROD\\b025527 /persistent:yes\n")
                # bat_file.write("net use Y: /delete\n")
                # bat_file.write("net use Y: \\\\10.48.196.73\\Data_1 rs@1809GEOD /user:PROD\\b025527 /persistent:yes\n")
                # bat_file.write("net use V: /delete\n")
                # bat_file.write("net use V: \\\\kmsload157.kmsext.dk\\data\\mapserver\\data YL9B64TMKq /user:b025527 /persistent:yes\n")

                bat_file.write("gdal_translate -of AAIGrid -projwin " + str(TLX - (float(RES) * 20)) + " " + str(TLY + (float(RES) * 20)) + " " + str(LRX + (float(RES) * 20)) + " " + str(
                    LRY - (float(RES) * 20)) + " F:\GDB\DHM\AnvendelseGIS\DTM_orto.vrt " + DEMpath + "\n")
                bat_file.write("C:\\dev\\COWS\\orto.exe -def " + defName + "\n")
                bat_file.write("gdal_translate -b 1 -b 2 -b 3 -a_srs EPSG:25832 -of GTIFF -co COMPRESS=JPEG -co JPEG_QUALITY=85 -co PHOTOMETRIC=YCBCR -co TILED=YES " + calcPath + OName + ' ' + jpegPath + OName + "\n")
                bat_file.write("REM *** Move Output *** \n")
                bat_file.write("copy " + jpegPath + OName + " " + finalDst + " \n")
                bat_file.write("IF %ERRORLEVEL% NEQ 0 (\n")
                bat_file.write("  ECHO Copy failed\n")
                sql_streng = "update " + schem + "." + tabl + " set qo_done = \'Fail\' WHERE imageid = \'" + ImageID + "\'"
                bat_file.write('  python C:/dev/GRU/reportPPC.py \"' + sql_streng + "\" \n")
                bat_file.write(") ELSE (\n")
                bat_file.write("  ECHO Copy succeded\n")
                sql_streng = "update " + schem + "." + tabl + " set qo_done = \'Done\' WHERE imageid = \'" + ImageID + "\'"
                bat_file.write('  python C:/dev/GRU/reportPPC.py \"' + sql_streng + "\" \n")
                sql_streng = "update " + schem + "." + tabl + " set comment = \'" + finalDst + OName + "\' WHERE imageid = \'" + ImageID + "\'"
                bat_file.write('  python C:/dev/GRU/reportPPC.py \"' + sql_streng + "\" \n")
                bat_file.write(")\n")
                bat_file.write("REM *** CleanUP *** \n")
                bat_file.write("del " + calcPath + "DTM_" + ImageID + ".*\n")
                bat_file.write("del " + calcPath + "O" + ImageID + ".*\n")
                bat_file.write("del " + jpegPath + "O" + ImageID + ".*\n")
                bat_file.write('python C:/dev/GRU/writeProgress.py ' + jobnavn + " 101 \n")
                dbkald = "update " + schem + "." + tabl + " set qo_done = \'Pending\' WHERE imageid = \'" + ImageID + "\'"
                print (dbkald)
                cur.execute(dbkald)
                conn.commit()

            createDef(defName, imgpath, DEMpath, ortName, IO, EO, Polyg, RES)
            print (BoBox)
            MinionManager('quick_orto', orto_batfil, 'GRU', BoBox)

        return 1, 'JobBuilt'

            #
            # *** End Create GRU Job ***
    except(psycopg2.ProgrammingError):
        print ('DB error getting image from PPC')
        return -1,'Error'

def GRU_filelist(schem,tabl,gsd):
    conn = setDB()
    cur = conn.cursor()
    #schem = 'remote_sensing'
    #tabl = 'oblique_footprints2019'
    if gsd == '0.10':
        outSti = '\\\\kmsload157.kmsext.dk\\data\\mapserver\\data\\ortofoto\\2019_quickorto\\10cm\\filelists\\'
    else:
        outSti = '\\\\kmsload157.kmsext.dk\\data\\mapserver\\data\\ortofoto\\2019_quickorto\\16cm\\filelists\\'

    cur = conn.cursor()
    dbkald1 = "select distinct a.kn10kmdk from remote_sensing.\"10km_tiles\" a, " + schem + "." + tabl + " b where ST_DWithin(a.geom, b.geom,2000) and b.qo_done = 'Done' and gsd = '" + gsd + "'"

    cur.execute(dbkald1)
    list1 = cur
    for i in list1:
        print (i[0])
        with open(outSti + i[0] + ".filelist", "w") as text_file:
            cur2 = conn.cursor()
            dbkald2 = "select distinct b.imageid from remote_sensing.\"10km_tiles\" a, " + schem + "." + tabl + " b where ST_DWithin(a.geom, b.geom,2000) and (b.qo_done = 'Done' or b.qo_done = 'Distrib') and a.kn10kmdk = '" + i[0] + "' and gsd = '" + gsd + "'"
            cur2.execute(dbkald2)
            list2 = cur2
            for j in list2:
                print (j)
                text_file.write('O' + j[0] + '.tif\n')
                cur3 = conn.cursor()
                dbkald3 = "update " + schem + "." + tabl + " set qo_done = \'Distrib\' WHERE imageid = \'" + j[0] + "\'"
                print(dbkald3)
                cur3.execute(dbkald3)
                conn.commit()
            text_file.close()
