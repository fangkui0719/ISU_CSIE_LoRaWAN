#!/usr/bin/env python2
# -*- coding: utf-8 -*-

''' Experiment
    1 : LoraWan Adaptive Data Rate Algorithm
    2 : EXPLoRa-AT Adaptive Data Rate Algorithm
    3 : EXPLoRa-TS Adaptive Data Rate Algorithm '''

import simpy
import random
import numpy as np
import math
import sys
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt_node_der
import os
import time
from matplotlib.patches import Rectangle

# do the full collision check
full_collision = False

# RSSI global values for antenna
dir_30 = 4
dir_90 = 2
dir_150 = -4
dir_180 = -3

# this is an array with measured values for sensitivity see paper, Table 3
sf7 = np.array([7, -126.5, -124.25, -120.75])
sf8 = np.array([8, -127.25, -126.75, -124.0])
sf9 = np.array([9, -131.25, -128.25, -127.5])
sf10 = np.array([10, -132.75, -130.25, -128.75])
sf11 = np.array([11, -134.5, -132.75, -128.75])
sf12 = np.array([12, -133.25, -132.25, -132.25])

#
# check for collisions at base station
# Note: called before a packet (or rather node) is inserted into the list
def checkcollision(packet):
    col = 0  # flag needed since there might be several collisions for packet
    # lost packets don't collide
    if packet.lost:
        return 0
    if packetsAtBS[packet.bs]:
        for other in packetsAtBS[packet.bs]:
            if other.id != packet.nodeid:
                # simple collision
                if frequencyCollision(packet, other.packet[packet.bs]) \
                        and sfCollision(packet, other.packet[packet.bs]):
                    if full_collision:
                        if timingCollision(packet, other.packet[packet.bs]):
                            # check who collides in the power domain
                            c = powerCollision(packet, other.packet[packet.bs])
                            # mark all the collided packets
                            # either this one, the other one, or both
                            for p in c:
                                p.collided = 1
                                if p == packet:
                                    col = 1
                        else:
                            # no timing collision, all fine
                            pass
                    else:
                        packet.collided = 1
                        other.packet[packet.bs].collided = 1  # other also got lost, if it wasn't lost already
                        col = 1
        return col
    return 0


#
# frequencyCollision, conditions
#
#        |f1-f2| <= 120 kHz if f1 or f2 has bw 500
#        |f1-f2| <=  60 kHz if f1 or f2 has bw 250
#        |f1-f2| <=  30 kHz if f1 or f2 has bw 125
def frequencyCollision(p1, p2):
    if (abs(p1.freq - p2.freq) <= 120 and (p1.bw == 500 or p2.freq == 500)):
        return True
    elif (abs(p1.freq - p2.freq) <= 60 and (p1.bw == 250 or p2.freq == 250)):
        return True
    else:
        if (abs(p1.freq - p2.freq) <= 30):
            return True
    return False


def sfCollision(p1, p2):
    if p1.sf == p2.sf:
        # p2 may have been lost too, will be marked by other checks
        return True
    return False


def powerCollision(p1, p2):
    powerThreshold = 6  # dB
    if abs(p1.rssi - p2.rssi) < powerThreshold:
        # packets are too close to each other, both collide
        # return both packets as casualties
        return (p1, p2)
    elif p1.rssi - p2.rssi < powerThreshold:
        # p2 overpowered p1, return p1 as casualty
        return (p1,)
    # p2 was the weaker packet, return it as a casualty
    return (p2,)


def timingCollision(p1, p2):
    # assuming p1 is the freshly arrived packet and this is the last check
    # we've already determined that p1 is a weak packet, so the only
    # way we can win is by being late enough (only the first n - 5 preamble symbols overlap)

    # assuming 8 preamble symbols
    Npream = 8

    # we can lose at most (Npream - 5) * Tsym of our preamble
    Tpreamb = 2 ** p1.sf / (1.0 * p1.bw) * (Npream - 5)

    # check whether p2 ends in p1's critical section
    p2_end = p2.addTime + p2.rectime
    p1_cs = env.now + Tpreamb
    if p1_cs < p2_end:
        # p1 collided with p2 and lost
        return True
    return False


# this function computes the airtime of a packet
# according to LoraDesignGuide_STD.pdf
#
def airtime(sf, cr, pl, bw):
    H = 0  # implicit header disabled (H=0) or not (H=1)
    DE = 0  # low data rate optimization enabled (=1) or not (=0)
    Npream = 8  # number of preamble symbol (12.25  from Utz paper)
    Tsym = (2.0 ** sf) / bw
    Tpream = (Npream + 4.25) * Tsym
    # print "sf", sf, " cr", cr, "pl", pl, "bw", bw
    payloadSymbNB = 8 + max(math.ceil((8.0 * pl - 4.0 * sf + 28 + 16 - 20 * H) / (4.0 * (sf - 2 * DE))) * (cr + 4), 0)
    Tpayload = payloadSymbNB * Tsym
    return Tpream + Tpayload

def EXPLoRaAT(sf_vec):
    sf_v = np.array(sf_vec)
    sf_o = ([0, 0, 0, 0, 0, 0])
    for i in range(0, len(sf_o)):
        sf_o[i] = sf_v[i]

    SF_old.append(sf_o)
    w = np.array([1.0, 1.83, 3.33, 6.67, 13.34, 24.04])
    q = np.array([1.0 / 1.0, 1.0 / 1.83, 1.0 / 3.33, 1.0 / 6.67, 1.0 / 13.34, 1.0 / 24.04])
    P = sf_v * w

    # Water Filling Algorithm
    old_p = 0
    p = 1
    while old_p != p:
        p_idx = local_peaks_indexes(P)
        p = old_p
        old_p = p_idx
        start = 0
        for i in range(0, len(p_idx)):
            count = (sum(P[start:(p_idx[i])] * q[start:(p_idx[i])])) / (sum(q[start:(p_idx[i])]))
            for j in range(start, p_idx[i]):
                P[j] = count
            start = p_idx[i]

    EXP_P.append(P)
    print "EXPLoRa-AT weight: ", P
    k_AT = P * q
    vec = ([0, 0, 0, 0, 0, 0])
    for i in range(0, len(k_AT)):
        vec[i] = round(k_AT[i])
    EXP_K.append(vec)
    print "EXPLoRa-AT SF: ", vec
    return vec


def local_peaks_indexes(P):
    P_vec = np.array(P)
    p = []
    for i in range(1, len(P_vec)):
        if P_vec[i] > P_vec[i-1]:
            p.append(i)
    p.append(6)
    return p


def EXPLoRaTS(ts_nodes, bs_id, t):
    ts_nodes = ts_nodes
    T = float(t)
    w = np.array([1.0, 2.0, 4.0, 8.0, 16.0, 32.0])
    q = np.array([1.0 / 1.0, 1.0 / 2.0, 1.0 / 4.0, 1.0 / 8.0, 1.0 / 16.0, 1.0 / 32.0])
    N_sym_sf = np.array([0, 0, 0, 0, 0, 0])

    bs_id = bs_id
    sf_o = ([0, 0, 0, 0, 0, 0])
    # Calculate Symbol Time
    for ts_nd in range(0, len(ts_nodes)):
        if ts_nodes[ts_nd].bs_rx[bs_id] == 1:
            MP = float(ts_nodes[ts_nd].period)
            PL = float(ts_nodes[ts_nd].plen)
            SF = float(ts_nodes[ts_nd].sf)
            N_mess = T / MP
            N_sym_mess = 8 + max(math.ceil((2.0 * PL - SF + 11) / SF) * 5, 0)
            N_sym_usr = N_sym_mess * N_mess
            N_sym_sf[int(SF - 7)] = N_sym_sf[int(SF - 7)] + N_sym_usr
            sf_o[int(SF - 7)] = sf_o[int(SF - 7)] + 1
            ts_nodes[ts_nd].symboltime = N_sym_usr
            print "Node ID:", ts_nodes[ts_nd].id, "Symbol Time:", N_sym_usr, "PLEN:", PL

    SF_old.append(sf_o)
    print "SF:", sf_o
    P = N_sym_sf * w

    # Water-filling Algorithm
    old_p = 0
    p = 1
    while old_p != p:
        p_idx = local_peaks_indexes(P)
        # print "p_idx=", p_idx
        p = old_p
        old_p = p_idx
        start = 0
        for i in range(0, len(p_idx)):
            count = (sum(P[start:(p_idx[i])] * q[start:(p_idx[i])])) / (sum(q[start:(p_idx[i])]))
            for j in range(start, p_idx[i]):
                P[j] = count
            start = p_idx[i]
        # print "EXPLoRa-TS weight: ", P

    EXP_P.append(P)

    k_TS = P * q
    print "EXPLoRa-TS K:", k_TS

    bucket_nodes = ([0, 0, 0, 0, 0, 0])
    for i in range(0, len(ts_nodes)):
        if ts_nodes[i].bs_rx[bs_id] == 1:
            bucket_nodes[ts_nodes[i].sf - 7] += 1

    print "buckets:", bucket_nodes
    for bucket_sf in range(0, 6):
        pbucket = k_TS
        print pbucket
        for ts_times in range(0, int(bucket_nodes[bucket_sf])):
            max_pl = 0
            max_pl_id = 0

            for nd in range(len(ts_nodes)):
                if ts_nodes[nd].bs_rx[bs_id] == 1:
                    if ts_nodes[nd].sf == (bucket_sf + 7):
                        if ts_nodes[nd].ts == 0:
                            if max_pl == 0:
                                max_pl = ts_nodes[nd].plen
                                max_pl_id = nd
                            else:
                                if ts_nodes[nd].overlap:
                                    if ts_nodes[max_pl_id].overlap:
                                        if ts_nodes[nd].plen > max_pl:
                                            max_pl = ts_nodes[nd].plen
                                            max_pl_id = nd
                                else:
                                    if ts_nodes[max_pl_id].overlap:
                                        max_pl = ts_nodes[nd].plen
                                        max_pl_id = nd
                                    else:
                                        if ts_nodes[nd].plen > max_pl:
                                            max_pl = ts_nodes[nd].plen
                                            max_pl_id = nd


            print "SF:", bucket_sf + 7, "pbucket:", pbucket[bucket_sf], "Symbol Time:", ts_nodes[max_pl_id].symboltime

            if ts_nodes[max_pl_id].symboltime <= pbucket[bucket_sf]:
                print "no change"
                pbucket[bucket_sf] = pbucket[bucket_sf] - ts_nodes[max_pl_id].symboltime
                ts_nodes[max_pl_id].ts = 1
            else:
                print "change sf"
                print "times", ts_times, "FIND ID:", max_pl_id, "PLEN:", max_pl
                ts_nodes[max_pl_id].sf += 1
                print "ID:", max_pl_id, "SF:", ts_nodes[max_pl_id].sf
                if bucket_sf < 5:
                    bucket_nodes[bucket_sf + 1] += 1
                MP = float(ts_nodes[max_pl_id].period)
                PL = float(ts_nodes[max_pl_id].plen)
                SF = float(ts_nodes[max_pl_id].sf)
                N_mess = T / MP
                N_sym_mess = 8 + max(math.ceil((2.0 * PL - SF + 11) / SF) * 5, 0)
                N_sym_usr = N_sym_mess * N_mess
                ts_nodes[max_pl_id].symboltime = N_sym_usr



        print pbucket

    no_ts_nodes = []
    for i in range(0, len(ts_nodes)):
        if ts_nodes[i].bs_rx[bs_id] == 1:
            if ts_nodes[i].ts == 0:
                no_ts_nodes.append(i)

    for ts_times in range(0, len(no_ts_nodes)):
        ts_nodes[int(no_ts_nodes[ts_times])].sf = ts_nodes[int(no_ts_nodes[ts_times])].initial_sf
        MP = float(ts_nodes[int(no_ts_nodes[ts_times])].period)
        PL = float(ts_nodes[int(no_ts_nodes[ts_times])].plen)
        SF = float(ts_nodes[int(no_ts_nodes[ts_times])].sf)
        N_mess = T / MP
        N_sym_mess = 8 + max(math.ceil((2.0 * PL - SF + 11) / SF) * 5, 0)
        N_sym_usr = N_sym_mess * N_mess
        ts_nodes[int(no_ts_nodes[ts_times])].symboltime = N_sym_usr

        for bucket_sf in range(int(ts_nodes[int(no_ts_nodes[ts_times])].sf - 7), 6):
            max_bucket_sf = int(ts_nodes[int(no_ts_nodes[ts_times])].sf - 7)
            max_bucket = pbucket[max_bucket_sf]
            if pbucket[bucket_sf] > max_bucket:
                max_bucket = pbucket[bucket_sf]
                max_bucket_sf = bucket_sf

        pbucket[max_bucket_sf] = pbucket[max_bucket_sf] - ts_nodes[int(no_ts_nodes[ts_times])].symboltime
        ts_nodes[int(no_ts_nodes[ts_times])].ts = 1

    sf_n = ([0, 0, 0, 0, 0, 0])


    for test in range(0, len(ts_nodes)):
        if ts_nodes[test].bs_rx[bs_id] == 1:
            sf_n[ts_nodes[test].sf - 7] += 1

    print sf_n
    for nd in range(0, len(ts_nodes)):
        if ts_nodes[nd].bs_rx[bs_id] == 1:
            if ts_nodes[nd].ts == 1:
                ts_nodes[nd].ts = 0

    print sf_o
    print sf_n
    print "right"
    return ts_nodes


#
# this function creates a BS
#
class myBS():
    def __init__(self, id):
        self.id = id
        self.x = 0
        self.y = 0

        # This is a hack for now
        global nrBS
        global maxDist
        global maxX
        global maxY
        global baseDist

        if (nrBS == 1 and self.id == 0):
            self.x = maxDist
            self.y = maxY

        if (nrBS == 2 and self.id == 0):
            self.x = maxDist
            self.y = maxY

        if (nrBS == 2 and self.id == 1):
            self.x = maxDist + baseDist
            self.y = maxY

        if (nrBS == 3 and self.id == 0):
            self.x = 0.0
            self.y = 0.0

        if (nrBS == 3 and self.id == 1):
            self.x = 0.0 + baseDist / 2.0
            self.y = 0.0 + (np.sqrt(3.0) * baseDist / 2.0)

        if (nrBS == 3 and self.id == 2):
            self.x = 0.0 + baseDist
            self.y = 0.0

        if (nrBS == 4 and self.id == 0):
            self.x = maxDist + baseDist
            self.y = maxY

        if (nrBS == 4 and self.id == 1):
            self.x = maxDist
            self.y = maxY

        if (nrBS == 4 and self.id == 2):
            self.x = maxDist + 2 * baseDist
            self.y = maxY

        if (nrBS == 4 and self.id == 3):
            self.x = maxDist + baseDist
            self.y = maxY + baseDist

        if (nrBS == 5 and self.id == 0):
            self.x = maxDist + baseDist
            self.y = maxY + baseDist

        if (nrBS == 5 and self.id == 1):
            self.x = maxDist
            self.y = maxY + baseDist

        if (nrBS == 5 and self.id == 2):
            self.x = maxDist + 2 * baseDist
            self.y = maxY + baseDist

        if (nrBS == 5 and self.id == 3):
            self.x = maxDist + baseDist
            self.y = maxY

        if (nrBS == 5 and self.id == 4):
            self.x = maxDist + baseDist
            self.y = maxY + 2 * baseDist

        if (nrBS == 6):
            if (self.id < 3):
                self.x = (self.id + 1) * maxX / 4.0
                self.y = maxY / 3.0
            else:
                self.x = (self.id + 1 - 3) * maxX / 4.0
                self.y = 2 * maxY / 3.0

        if (nrBS == 8):
            if (self.id < 4):
                self.x = (self.id + 1) * maxX / 5.0
                self.y = maxY / 3.0
            else:
                self.x = (self.id + 1 - 4) * maxX / 5.0
                self.y = 2 * maxY / 3.0

        if (nrBS == 24):
            if (self.id < 8):
                self.x = (self.id + 1) * maxX / 9.0
                self.y = maxY / 4.0
            elif (self.id < 16):
                self.x = (self.id + 1 - 8) * maxX / 9.0
                self.y = 2 * maxY / 4.0
            else:
                self.x = (self.id + 1 - 16) * maxX / 9.0
                self.y = 3 * maxY / 4.0

        if (nrBS == 96):
            if (self.id < 24):
                self.x = (self.id + 1) * maxX / 25.0
                self.y = maxY / 5.0
            elif (self.id < 48):
                self.x = (self.id + 1 - 24) * maxX / 25.0
                self.y = 2 * maxY / 5.0
            elif (self.id < 72):
                self.x = (self.id + 1 - 48) * maxX / 25.0
                self.y = 3 * maxY / 5.0
            else:
                self.x = (self.id + 1 - 72) * maxX / 25.0
                self.y = 4 * maxY / 5.0

        print "BSx:", self.x, "BSy:", self.y


#
# this function creates a node
#
class myNode():
    def __init__(self, id, myBS, type):
        global bs
        global experiment
        global Ptx
        global gamma
        global d0
        global var
        global Lpld0
        global GL
        global maxDist

        self.bs = myBS      # Center Base Station
        self.id = id
        self.x = 0
        self.y = 0

        self.dist = []
        self.packet = []
        self.bs_rx = []
        self.bs_sf = []

        self.minBS = self.bs.id

        self.ts = 0
        self.symboltime = 0

        for i in range(0, nrBS):
            self.bs_rx.append(0)
            self.bs_sf.append(7)

        self.overlap = False

        if type == 1:
            self.type = "aggressive"
            self.period = random.randint(30000, 60000)
            self.plen = random.randint(120, 160)
            node_d = 0.4 * maxDist
        if type == 2:
            self.type = "non-aggressive"
            self.period = random.randint(600000, 1800000)
            self.plen = random.randint(20, 40)
            node_d = 0.6 * maxDist

        self.sf = 7
        self.cr = 1
        self.bw = 125

        # this is very complex prodecure for placing nodes and ensure minimum distance between each pair of nodes
        found = 0
        rounds = 0
        global nodes
        while found == 0 and rounds < 100:
            global maxX
            global maxY
            a = random.random()
            b = random.random()
            if b < a:
                a, b = b, a
            posx = b * node_d * math.cos(2 * math.pi * a / b) + self.bs.x
            posy = b * node_d * math.sin(2 * math.pi * a / b) + self.bs.y

            if type == 2:
                slide = np.sqrt(((posx - float(self.bs.x)) ** 2) + ((posy - float(self.bs.y)) ** 2))
                newx = ((slide + 0.4 * maxDist) * ((posx - float(self.bs.x)) / slide)) + self.bs.x
                newy = ((slide + 0.4 * maxDist) * ((posy - float(self.bs.y)) / slide)) + self.bs.y
                posx = newx
                posy = newy

            if len(nodes) > 0:
                for index, n in enumerate(nodes):
                    dist = np.sqrt(((abs(n.x - posx)) ** 2) + ((abs(n.y - posy)) ** 2))
                    # we set this so nodes can be placed everywhere
                    # otherwise there is a risk that little nodes are placed
                    # between the base stations where it would be more crowded
                    if dist >= 0:
                        found = 1
                        self.x = posx
                        self.y = posy
                    else:
                        rounds = rounds + 1
                        if rounds == 100:
                            print "could not place new node, giving up"
                            exit(-2)
            else:
                self.x = posx
                self.y = posy
                found = 1

        # Optimize SF and choose the faster SF
        mindist = 99999
        for i in range(0, nrBS):
            distance = np.sqrt((self.x - bs[i].x) * (self.x - bs[i].x)
                               + (self.y - bs[i].y) * (self.y - bs[i].y))
            if distance < mindist:
                mindist = distance
                self.minBS = i
            self.dist.append(distance)
            Lpl = Lpld0 + 10 * gamma * math.log10(distance / d0)
            Prx = Ptx - GL - Lpl
            minairtime = 9999
            minsf = 0
            for j in range(0, 6):
                if sensi[j, 1] < Prx:
                    self.sf = int(sensi[j, 0])
                    at = airtime(self.sf, self.cr, self.plen, self.bw)
                    if at < minairtime:
                        minairtime = at
                        minsf = self.sf
                        minsensi = sensi[j, 1]

            if minairtime == 9999:
                minsf = 12

            self.bs_sf[i] = minsf

        sf_check = np.array(self.bs_sf)
        self.sf = np.amin(sf_check)

        for i in range(0, nrBS):
            self.packet.append(myPacket(self.id, self.plen, self.dist[i], i, self.sf))

            if self.packet[i].lost:
                self.bs_rx[i] = 0
            else:
                self.bs_rx[i] = 1

        print('node %d' % id, "x", self.x, "y", self.y, "dist: ", self.dist, "BS: ", self.bs.id, "Type: ", type)

        bs_rx_count = 0
        for i in range(0, len(self.bs_rx)):
            if self.bs_rx[i] == 1:
                bs_rx_count = bs_rx_count + 1
        if bs_rx_count > 1:
            self.overlap = True

        if experiment == 3:
            self.initial_sf = self.sf

        self.sent = 0
        self.der = 0

    #
    #   update RSSI depending on direction
    #
    def updateRSSI(self):
        global bs

        #print "+++++++++uR node", self.id, " and bs ", self.bs.id
        #print "node x,y", self.x, self.y
        #print "main-bs x,y", bs[self.bs.id].x, bs[self.bs.id].y

        for i in range(0, len(self.packet)):
            #print "rssi before", self.packet[i].rssi
            #print "packet bs", self.packet[i].bs
            #print "packet bs x, y:", bs[self.packet[i].bs].x, bs[self.packet[i].bs].y
            if self.bs.id == self.packet[i].bs:
                #print "packet to main bs, increase rssi "
                self.packet[i].rssi = self.packet[i].rssi + dir_30
            else:
                b1 = np.array([bs[self.bs.id].x, bs[self.bs.id].y])
                p = np.array([self.x, self.y])
                b2 = np.array([bs[self.packet[i].bs].x, bs[self.packet[i].bs].y])

                ba = b1 - p
                bc = b2 - p
                #print ba
                #print bc

                cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
                angle = np.degrees(np.arccos(cosine_angle))

                #print "angle: ", angle

                if angle <= 30:
                    #print "rssi increase to other BS: 4"
                    self.packet[i].rssi = self.packet[i].rssi + dir_30
                elif angle <= 90:
                    #print "rssi increase to other BS: 2"
                    self.packet[i].rssi = self.packet[i].rssi + dir_90
                elif angle <= 150:
                    #print "rssi increase to other BS: -4"
                    self.packet[i].rssi = self.packet[i].rssi + dir_150
                else:
                    #print "rssi increase to other BS: -3"
                    self.packet[i].rssi = self.packet[i].rssi + dir_180
            #print "packet rssi after", self.packet[i].rssi


#
# this function creates a packet (associated with a node)
# it also sets all parameters, currently random
#
class myPacket():
    def __init__(self, nodeid, plen, distance, bs, sf):
        global experiment
        global Ptx
        global gamma
        global d0
        global var
        global Lpld0
        global GL
        global nodes

        self.bs = bs
        self.nodeid = nodeid

        self.sf = sf
        self.cr = 1
        self.bw = 125
        self.plen = plen

        self.rectime = airtime(self.sf, self.cr, self.plen, self.bw)

        Lpl = Lpld0 + 10 * gamma * math.log10(distance / d0)
        Prx = Ptx - GL - Lpl

        # transmission range, needs update XXX
        self.transRange = 150
        self.symTime = (2.0 ** self.sf) / self.bw
        self.arriveTime = 0
        self.rssi = Prx
        # frequencies: lower bound + number of 61 Hz steps
        self.freq = 860000000
        # denote if packet is collided
        self.collided = 0
        self.processed = 0

        global minsensi
        self.lost = self.rssi < minsensi
        if self.lost:
            if sensi_125[self.sf - 7] < self.rssi:
                self.lost = True

        # print "node {} bs {} lost {}".format(self.nodeid, self.bs, self.lost)

#
# main discrete event loop, runs for each node
# a global list of packet being processed at the gateway
# is maintained
#
def transmit(env, node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        yield env.timeout(random.expovariate(1.0 / float(node.period)))

        # time sending and receiving
        # packet arrives -> add to base station

        node.sent = node.sent + 1

        sf_sent[node.sf - 7] = sf_sent[node.sf - 7] + 1

        global packetSeq
        packetSeq = packetSeq + 1

        global nrBS
        for bs in range(0, nrBS):
            if node in packetsAtBS[bs]:
                print "ERROR: packet already in"
            else:
                # adding packet if no collision
                if checkcollision(node.packet[bs]) == 1:
                    node.packet[bs].collided = 1
                else:
                    node.packet[bs].collided = 0
                packetsAtBS[bs].append(node)
                node.packet[bs].addTime = env.now
                node.packet[bs].seqNr = packetSeq

        # take first packet rectime
        yield env.timeout(node.packet[0].rectime)

        # if packet did not collide, add it in list of received packets
        # unless it is already in
        for bs in range(0, nrBS):
            if node.packet[bs].lost:
                lostPackets.append(node.packet[bs].seqNr)
            else:
                if node.packet[bs].collided == 0:
                    if nrNetworks == 1:
                        packetsRecBS[bs].append(node.packet[bs].seqNr)
                    else:
                        # now need to check for right BS
                        if node.bs.id == bs:
                            packetsRecBS[bs].append(node.packet[bs].seqNr)
                    # recPackets is a global list of received packets
                    # not updated for multiple networks
                    if recPackets:
                        if recPackets[-1] != node.packet[bs].seqNr:
                            recPackets.append(node.packet[bs].seqNr)
                            packetsRecNodes[node.packet[bs].sf - 7].append(node.packet[bs].seqNr)
                            packetsRecED[node.packet[bs].nodeid].append(node.packet[bs].seqNr)
                    else:
                        recPackets.append(node.packet[bs].seqNr)
                        packetsRecNodes[node.packet[bs].sf - 7].append(node.packet[bs].seqNr)
                        packetsRecED[node.packet[bs].nodeid].append(node.packet[bs].seqNr)

                else:
                    # XXX only for debugging
                    collidedPackets.append(node.packet[bs].seqNr)

        # complete packet has been received by base station
        # can remove it

        for bs in range(0, nrBS):
            if node in packetsAtBS[bs]:
                packetsAtBS[bs].remove(node)
                # reset the packet
                node.packet[bs].collided = 0
                node.packet[bs].processed = 0

#
# "main" program
#
# get arguments
if len(sys.argv) == 11:
    nrNodes = int(sys.argv[1])
    avgSendTime = int(sys.argv[2])
    experiment = int(sys.argv[3])
    simtime = int(sys.argv[4])
    nrBS = int(sys.argv[5])
    if len(sys.argv) > 6:
        full_collision = bool(int(sys.argv[6]))
    directionality = int(sys.argv[7])
    nrNetworks = int(sys.argv[8])
    baseDist = float(sys.argv[9])
    p_value = float(sys.argv[10])
    print "Nodes per base station:", nrNodes
    print "AvgSendTime (exp. distributed):", avgSendTime
    print "Experiment: ", experiment
    print "Simtime: ", simtime
    print "nrBS: ", nrBS
    print "Full Collision: ", full_collision
    print "with directionality: ", directionality
    print "nrNetworks: ", nrNetworks
    print "baseDist: ", baseDist  # x-distance between the two base stations
    print "p value: ", p_value

else:
    print "Error!"
    exit(-1)

# global stuff
nodes = []
#packetsAtBS = []

ts_symbol_time = 0

SF_old = []
SF_new = []
EXP_P = []
EXP_K = []

env = simpy.Environment()

# max distance: 300m in city, 3000 m outside (5 km Utz experiment)
# also more unit-disc like according to Utz
nrCollisions = 0
nrReceived = 0
nrProcessed = 0

# global value of packet sequence numbers
packetSeq = 0

# list of received packets
recPackets = []
collidedPackets = []
lostPackets = []

Ptx = 14
gamma = 2.08
d0 = 40.0
var = 0  # variance ignored for now
Lpld0 = 127.41
GL = 0

sensi = np.array([sf7, sf8, sf9, sf10, sf11, sf12])

# figure out the minimal sensitivity for the given experiment
sensi_125 = np.array([-126.5, -127.25, -131.25, -132.75, -134.5, -133.25])
minsensi = np.amin(sensi_125)

Lpl = Ptx - minsensi
print "amin", minsensi, "Lpl", Lpl
maxDist = d0 * (10 ** ((Lpl - Lpld0) / (10.0 * gamma)))
#maxDist = d0*(math.e**((Lpl-Lpld0)/(10.0*gamma)))
print "maxDist:", maxDist

# size of area
xmax = maxDist * (nrBS + 2) + 20
ymax = maxDist * (nrBS + 1) + 20

# maximum number of packets the BS can receive at the same time
maxBSReceives = 8

maxX = maxDist + baseDist * nrBS
print "maxX ", maxX
maxY = 2 * maxDist * math.sin(30 * (math.pi / 180))  # == maxdist
print "maxY", maxY

# list of base stations
bs = []

# list of packets at each base station, init with 0 packets
packetsAtBS = []
packetsRecBS = []
packetsRecED = []
for i in range(0, nrBS):
    b = myBS(i)
    bs.append(b)
    packetsAtBS.append([])
    packetsRecBS.append([])

for i in range(0, nrNodes * nrBS):
    packetsRecED.append([])

packetsRecNodes = []
sf_sent = ([0, 0, 0, 0, 0, 0])
for i in range(0, 7):
    packetsRecNodes.append([])

if experiment == 1:
    nodes_p = int(nrNodes * p_value)
    print "aggressive node: ", nodes_p
    for i in range(0, nrNodes):
        # myNode takes period (in ms), base station id packetlen (in Bytes)
        # 1000000 = 16 min
        if i < nodes_p:
            type = 1
        else:
            type = 2
        for j in range(0, nrBS):
            # create nrNodes for each base station
            node = myNode(i * nrBS + j, bs[j], type)
            nodes.append(node)

            # when we add directionality, we update the RSSI here
            if directionality == 1:
                node.updateRSSI()

            env.process(transmit(env, node))

# EXPLoRa Algorithm
# experiment 2 -> EXPLoRa-AT
# experiment 3 -> EXPLoRa-TS
if experiment == 2:
    # Create nodes
    nodes_num = int(nrNodes * p_value)

    for i in range(0, nrNodes):
        # myNode takes period (in ms), base station id packetlen (in Bytes)
        # 1000000 = 16 min
        if i < nodes_num:
            type = 1
        else:
            type = 2
        for j in range(0, nrBS):
            # create nrNodes for each base station
            node = myNode(i * nrBS + j, bs[j], type)
            nodes.append(node)

            # when we add directionality, we update the RSSI here
            if directionality == 1:
                node.updateRSSI()

    for i in range(0, len(nodes)):
        print "id:", nodes[i].id, "sf:", nodes[i].sf

    for bsid in range(0, nrBS):
        SF_vec = ([0, 0, 0, 0, 0, 0])
        for i in range(0, len(nodes)):
            if int(nodes[i].bs_rx[bsid]) == 1:
                SF_vec[nodes[i].sf - 7] += 1

        if bsid < nrBS - 1:
            next_bs = bsid + 1
        else:
            next_bs = 0

        center_x = (bs[bsid].x + bs[next_bs].x) / 2
        center_y = (bs[bsid].y + bs[next_bs].y) / 2
        np.sqrt((bs[bsid].x - center_x) * (bs[bsid].x - center_x) + (bs[bsid].y - center_y) * (bs[bsid].y - center_y))

        exp_sf = EXPLoRaAT(SF_vec)
        new_sf_list = exp_sf
        sf_temp = SF_vec
        exp_cnt = 0
        sf_check = 0
        dev = []

        for i in range(0, 6):
            sf_check = sf_check + sf_temp[i]
            exp_cnt = exp_cnt + new_sf_list[i]

        if exp_cnt > sf_check:
            for i in range(0, 5):
                dev_tmp = round((exp_cnt - sf_check) * new_sf_list[i] / exp_cnt)
                dev.append(dev_tmp)
            for i in range(0, 5):
                new_sf_list[i] = new_sf_list[i] - int(dev[i])

        for i in range(0, 5):
            if sf_temp[i] > new_sf_list[i]:
                count = int(sf_temp[i] - new_sf_list[i])
                for num in range(0, count):
                    min_dist_id = 0
                    min_dist = 0
                    for j in range(0, len(nodes)):
                        if nodes[j].bs_rx[bsid] == 1:
                            if nodes[j].sf == i + 7:
                                check_dist = np.sqrt((nodes[j].x - center_x) * (nodes[j].x - center_x) + (nodes[j].y - center_y) * (nodes[j].y - center_y))
                                if min_dist == 0:
                                    min_dist = check_dist
                                    min_dist_id = j
                                else:
                                    if check_dist >= min_dist:
                                        min_dist = check_dist
                                        min_dist_id = j

                    nodes[min_dist_id].sf = nodes[min_dist_id].sf + 1
                    for bs_tmp in range(0, nrBS):
                        nodes[min_dist_id].packet[bs_tmp].sf = nodes[min_dist_id].packet[bs_tmp].sf + 1
                    sf_temp[i] = sf_temp[i] - 1
                    sf_temp[i + 1] = sf_temp[i + 1] + 1

        for nd in range(0, len(nodes)):
            # Update Packets
            global sensi_125
            for bs_tmp in range(0, nrBS):
                nodes[nd].packet[bs_tmp].symTime = (2.0 ** nodes[nd].packet[bs_tmp].sf) / nodes[nd].packet[bs_tmp].bw
                nodes[nd].packet[bs_tmp].lost = nodes[nd].packet[bs_tmp].rssi < sensi_125[nodes[nd].packet[bs_tmp].sf - 7]

                if nodes[nd].packet[bs_tmp].lost:
                    nodes[nd].bs_rx[bs_tmp] = 0
                else:
                    nodes[nd].bs_rx[bs_tmp] = 1

            bs_rx_count = 0
            for i in range(0, len(nodes[nd].bs_rx)):
                if nodes[nd].bs_rx[i] == 1:
                    bs_rx_count = bs_rx_count + 1
            if bs_rx_count > 1:
                nodes[nd].overlap = True
    for nd_start in range(0, len(nodes)):
        # print "node {} bs {} lost {}".format(self.nodeid, self.bs, self.lost)
        env.process(transmit(env, nodes[nd_start]))

if experiment == 3:
    # Create nodes
    nodes_num = int(nrNodes * p_value)
    print "aggressive node: ", nodes_num

    for i in range(0, nrNodes):
        # myNode takes period (in ms), base station id packetlen (in Bytes)
        # 1000000 = 16 min
        if i < nodes_num:
            type = 1
        else:
            type = 2
        for j in range(0, nrBS):
            # create nrNodes for each base station
            node = myNode(i * nrBS + j, bs[j], type)
            nodes.append(node)

            # when we add directionality, we update the RSSI here
            if directionality == 1:
                node.updateRSSI()

    for bsid in range(0, nrBS):
        SF_vec = ([0, 0, 0, 0, 0, 0])
        for nd in range(0, len(nodes)):
            if nodes[nd].bs_rx[bsid] == 1:
                SF_vec[nodes[nd].sf - 7] += 1

        exp_nodes = EXPLoRaTS(nodes, bsid, simtime)
        nodes = exp_nodes

    for nd_num in range(0, len(nodes)):
        # Update Packets
        global sensi_125
        for bs_tmp in range(0, nrBS):
            nodes[nd_num].packet[bs_tmp].sf = nodes[nd_num].sf
            nodes[nd_num].packet[bs_tmp].symTime = (2.0 ** nodes[nd_num].packet[bs_tmp].sf) / nodes[nd_num].packet[bs_tmp].bw
            nodes[nd_num].packet[bs_tmp].lost = nodes[nd_num].packet[bs_tmp].rssi < sensi_125[nodes[nd_num].packet[bs_tmp].sf - 7]

            if nodes[nd_num].packet[bs_tmp].lost:
                nodes[nd_num].bs_rx[bs_tmp] = 0

            else:
                nodes[nd_num].bs_rx[bs_tmp] = 1

        bs_rx_count = 0
        for i in range(0, len(nodes[nd_num].bs_rx)):
            if nodes[nd_num].bs_rx[i] == 1:
                bs_rx_count = bs_rx_count + 1
        if bs_rx_count > 1:
            nodes[nd_num].overlap = True
        #print "node {} bs {} lost {}".format(self.nodeid, self.bs, self.lost)
        env.process(transmit(env, nodes[nd_num]))

# start simulation
env.run(until=simtime)

for i in range(0, len(packetsRecED)):
    if int(nodes[i].sent) == 0:
        nodes[i].der = 0
    else:
        nodes[i].der = float(float(len(packetsRecED[i])) / float(nodes[i].sent))

# store nodes and basestation locationsEXPLoRa
with open('nodes.txt', 'w') as nfile:
    for node in nodes:
        nfile.write('{id} {x} {y} {sf} {type} {der}\n'.format(**vars(node)))

with open('basestation.txt', 'w') as bfile:
    for basestation in bs:
        bfile.write('{id} {x} {y}\n'.format(**vars(basestation)))

print "========================================================================"
print "Simulation time:", env.now, "( ms )"

sum = 0
for i in range(0, nrBS):
    #print "packets at BS", i, ":", len(packetsRecBS[i])
    sum = sum + len(packetsRecBS[i])
#print "sent packets: ", packetSeq
#print "overall received at right BS: ", sum

sumSent = 0
sent = []
for i in range(0, nrBS):
    sent.append(0)
for i in range(0, nrNodes * nrBS):
    sumSent = sumSent + nodes[i].sent
    #print "id for node ", nodes[i].id, "BS:", nodes[i].bs.id, " sent: ", nodes[i].sent
    sent[nodes[i].bs.id] = sent[nodes[i].bs.id] + nodes[i].sent
#for i in range(0, nrBS):
    #print "send to BS[", i, "]:", sent[i]

der = []
derALL = float(len(recPackets)) / float(sumSent)
sumder = 0

for i in range(0, nrBS):
    der.append(len(packetsRecBS[i]) / float(sent[i]))
    #print "DER BS[", i, "]:", der[i]
    sumder = sumder + der[i]
avgDER = (sumder) / nrBS
#print "sum DER: ", sumder
#print "avg DER: ", avgDER

for bsid in range(0, nrBS):
    SF_n = ([0, 0, 0, 0, 0, 0])
    for nd in range(0, len(nodes)):
        if nodes[nd].bs_rx[bsid] == 1:
            SF_n[nodes[nd].sf - 7] += 1
    SF_new.append(SF_n)

if experiment == 1:
    SF_total = ([0, 0, 0, 0, 0, 0])
    for i in range(0, len(nodes)):
        SF_total[nodes[i].sf - 7] += 1
    print "Experiment:", experiment, "( LoRaWAN ADR Function )"
    print "Spreading Factor ( SF ):", SF_total
    print "========================================================================"

    for i in range(0, nrBS):
        print "BS", i, "SF: ", SF_new[i]


if experiment == 2 or experiment == 3:
    SF_total = ([0, 0, 0, 0, 0, 0])
    for i in range(0, len(nodes)):
        SF_total[nodes[i].sf - 7] += 1
    if experiment == 2:
        print "Experiment:", experiment, "( EXPLoRa-AT Algorithm )"
    elif experiment == 3:
        print "Experiment:", experiment, "( EXPLoRa-TS Algorithm )"
    print "Spreading Factor ( SF ):", SF_total
    print "========================================================================"

    for i in range(0, nrBS):
        print "BS", i, ":", SF_old[i], "\t>> ", SF_new[i]

print "========================================================================"
print "Packets (   Sent   ):", sumSent
print "Packets ( Received ):", len(recPackets)
print "Packets ( Collided ):", len(collidedPackets)
print "Packets (   Lost   ):", len(lostPackets)
print "Data Extraction Rate ( DER ):", derALL
print "========================================================================"
sf_s = []
sf_r = []
sf_d = []

for i in range(0, 6):
    if sf_sent[i] == 0 or len(packetsRecNodes[i]) == 0:
        print "SF = ", i + 7, "\tsent:", sf_sent[i], "\treceived:", len(packetsRecNodes[i]), "\tDER:", str(0.0)
        sf_s.append(sf_sent[i])
        sf_r.append(len(packetsRecNodes[i]))
        sf_d.append(0.0)
    else:
        print "SF = ", i+7, "\tsent:", sf_sent[i], "\treceived:", len(packetsRecNodes[i]), "\tDER:", float(len(packetsRecNodes[i]))/float(sf_sent[i])
        sf_s.append(sf_sent[i])
        sf_r.append(len(packetsRecNodes[i]))
        sf_d.append(float(len(packetsRecNodes[i]))/float(sf_sent[i]))

# Trace File
fname = "/home/lab-3714/LoRaSim/Output/Method3/exp" + str(experiment) + "d99" + "BS" + str(nrBS) + "Intf.csv"
#print "Trace File:dr", fname, ", basestation.txt, nodes.txt, nodes.jpg"
totalnodes = nrNodes * nrBS
if os.path.isfile(fname):
    csv = "\n" + str(totalnodes) + "," + str(nrBS) + "," + str(experiment) + "," + str(p_value) + "," + str(
        baseDist) + "," + str(avgSendTime) \
          + "," + str(simtime) + "," + str(derALL) + "," + str(sf_d[0]) + "," + str(sf_d[1]) + "," + str(
        sf_d[2]) + "," + str(sf_d[3]) + "," + str(sf_d[4]) + "," + str(sf_d[5])
else:
    csv = "nrNodes,nrBS,EXPERIMENT,P_VALUE,BS_DIST,PERIOD,SIM_TIME,DER,SF7_DER,SF8_DER,SF9_DER,SF10_DER,SF11_DER,SF12_DER\n" + str(
        totalnodes) + "," + str(nrBS) + "," + str(experiment) + "," + str(p_value) + "," + str(baseDist) + "," + str(
        avgSendTime) \
          + "," + str(simtime) + "," + str(derALL) + "," + str(sf_d[0]) + "," + str(sf_d[1]) + "," + str(
        sf_d[2]) + "," + str(sf_d[3]) + "," + str(sf_d[4]) + "," + str(sf_d[5])
with open(fname, "a") as myfile:
    myfile.write(csv)
myfile.close()

# Print nodes position
if p_value == 0.3:
    if baseDist == 100:
        plt.xlim(-600, 1000)
        plt.ylim(-600, 1000)
    elif baseDist == 500:
        plt.xlim(-600, 1400)
        plt.ylim(-600, 1400)
    else:
        plt.xlim(-600, 1800)
        plt.ylim(-600, 1800)

    file_read = open("/home/lab-3714/LoRaSim/basestation.txt")
    str_line = file_read.readline()

    node_0_x = []
    node_0_y = []
    node_7_x = []
    node_7_y = []
    node_8_x = []
    node_8_y = []
    node_9_x = []
    node_9_y = []
    node_10_x = []
    node_10_y = []
    node_11_x = []
    node_11_y = []
    node_12_x = []
    node_12_y = []

    while str_line:
        node = str_line.split(' ')
        if node[0] != ' ':
            node_0_x.append(node[1])
            node_0_y.append(node[2])
            #plt.scatter(node[1], node[2], color='r')
        str_line = file_read.readline()
    file_read.close()

    file_read = open("/home/lab-3714/LoRaSim/nodes.txt")
    str_line = file_read.readline()
    while str_line:
        node = str_line.split(' ')
        if node[0] != ' ':
            if(node[3] == '7'):
                node_7_x.append(node[1])
                node_7_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF7', color='black')
            elif (node[3] == '8'):
                node_8_x.append(node[1])
                node_8_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF8', color='b')
            elif (node[3] == '9'):
                node_9_x.append(node[1])
                node_9_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF9', color='g')
            elif (node[3] == '10'):
                node_10_x.append(node[1])
                node_10_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF10', color='c')
            elif (node[3] == '11'):
                node_11_x.append(node[1])
                node_11_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF11', color='y')
            elif (node[3] == '12'):
                node_12_x.append(node[1])
                node_12_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF12', color='purple')
        str_line = file_read.readline()
    plt.scatter(node_7_x, node_7_y, label='SF7', color='black')
    plt.scatter(node_8_x, node_8_y, label='SF8', color='b')
    plt.scatter(node_9_x, node_9_y, label='SF9', color='g')
    plt.scatter(node_10_x, node_10_y, label='SF10', color='c')
    plt.scatter(node_11_x, node_11_y, label='SF11', color='y')
    plt.scatter(node_12_x, node_12_y, label='SF12', color='purple')
    plt.scatter(node_0_x, node_0_y, label='gateway', color='red')
    plt.legend(loc=0)
    picturename = "/home/lab-3714/LoRaSim/Output/Method3/Figure/Exp-" + str(experiment) + "-nodes-loc-" + str(time.strftime("%Y%m%d-%H%M%S", time.localtime())) + ".png"
    plt.savefig(picturename)
    plt.cla()
    file_read.close()

    file_read = open("/home/lab-3714/LoRaSim/nodes.txt")

    if baseDist == 100:
        plt.xlim(-600, 1000)
        plt.ylim(-600, 1000)
    elif baseDist == 500:
        plt.xlim(-600, 1400)
        plt.ylim(-600, 1400)
    else:
        plt.xlim(-600, 1800)
        plt.ylim(-600, 1800)

    der_7_x = []
    der_7_y = []
    der_8_x = []
    der_8_y = []
    der_9_x = []
    der_9_y = []
    der_10_x = []
    der_10_y = []
    der_11_x = []
    der_11_y = []

    str_line = file_read.readline()
    while str_line:
        node = str_line.split(' ')
        if node[5] != ' ':
            if(float(node[5]) >= 0.0 and float(node[5]) < 0.2):
                der_7_x.append(node[1])
                der_7_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF7', color='r')
            if (float(node[5]) >= 0.2 and float(node[5]) < 0.4):
                der_8_x.append(node[1])
                der_8_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF7', color='orange')
            if (float(node[5]) >= 0.4 and float(node[5]) < 0.6):
                der_9_x.append(node[1])
                der_9_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF7', color='y')
            if (float(node[5]) >= 0.6 and float(node[5]) < 0.8):
                der_10_x.append(node[1])
                der_10_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF7', color='g')
            if (float(node[5]) >= 0.8 and float(node[5]) < 1.0):
                der_11_x.append(node[1])
                der_11_y.append(node[2])
                #plt.scatter(node[1], node[2], label='SF7', color='b')
        str_line = file_read.readline()
    plt.scatter(der_7_x, der_7_y, label='0.0-0.2', color='r')
    plt.scatter(der_8_x, der_8_y, label='0.2-0.4', color='orange')
    plt.scatter(der_9_x, der_9_y, label='0.4-0.6', color='y')
    plt.scatter(der_10_x, der_10_y, label='0.6-0.8', color='g')
    plt.scatter(der_11_x, der_11_y, label='0.8-1.0', color='b')
    plt.scatter(node_0_x, node_0_y, label='gateway', color='black')
    plt.legend(loc=0)
    picturename2 = "/home/lab-3714/LoRaSim/Output/Method3/Figure/Exp-" + str(experiment) + "-nodes-der-" + str(time.strftime("%Y%m%d-%H%M%S", time.localtime())) + ".png"
    plt.savefig(picturename2)
    file_read.close()
