# -*- coding:utf-8 -*- 
# @Time		:2019/2/1 2:36 PM
# @Author	:Coast Cao

import soundfile as sf
from argparse import ArgumentParser as ARP
import os
import glob
import shutil
from nnmnkwii.preprocessing import interp1d
import numpy as np

bin = "build/"

def get_config(sr):
    if(sr == 16000):
        nFFTHalf=1024
        alpha=0.58
        bap_dim=1
    elif(sr == 22050):
        nFFTHalf=1024
        alpha=0.65
        bap_dim=2
    elif(sr == 44100):
        nFFTHalf=2048
        alpha=0.76
        bap_dim=5
    elif(sr == 48000):
        nFFTHalf=2048
        alpha=0.77
        bap_dim=5
    else:
        raise ValueError("unsupported sampling rate:%d" % sr)

    return nFFTHalf, alpha, bap_dim

def get_dir(dr):
    f0_dir = os.path.join(dr, "f0")
    sp_dir = os.path.join(dr, "sp")
    bapd_dir = os.path.join(dr, "bapd")

    return f0_dir,sp_dir,bapd_dir

def analyse(args, mcsize, preprocess=True, interpolate=True):
    f0_dir, sp_dir, bapd_dir = get_dir(args.dr)
    for d in [f0_dir, sp_dir, bapd_dir]:
        if (os.path.exists(d)):
            shutil.rmtree((d))
        os.makedirs(d)

    nFFTHalf, alpha, bap_dim = get_config(args.sr)

    wavfiles = glob.glob(os.path.join(args.dr, "wav/*.wav"))

    for wavfile in wavfiles:
        fn = os.path.basename(wavfile).split(".")[0]
        os.system("%s/analysis %s %s/%s.raw.f0 %s/%s.raw.sp %s/%s.raw.bapd" %
                  (bin, wavfile, f0_dir, fn, sp_dir,
                   fn, bapd_dir, fn))
        f0_file = os.path.join(f0_dir, "%s.raw.f0" % fn)

        if(interpolate):
            f0 = np.fromfile(f0_file, dtype=np.float64)
            f0c = interp1d(f0, kind="slinear")
            f0c_file = os.path.join(f0_dir, "%s.interp.f0" % fn)
            f0c.tofile(f0c_file)
            f0_file = f0c_file


        if (preprocess):
            # convert f0 to lf0
            os.system("%s/x2x +da %s > %s/%s.raw.f0a" % (bin, f0_file, f0_dir, fn))
            os.system("%s/x2x +af %s/%s.raw.f0a | %s/sopr -magic 0.0 -LN -MAGIC -1.0E+10 > %s/%s.lf0" % (bin, f0_dir, fn, bin, f0_dir, fn))

            # convert sp to mgc
            os.system("%s/x2x +df %s/%s.raw.sp | %s/sopr -R -m 32768.0 | %s/mcep -a %f -m %d -l %d -e 1.0E-8 -j 0 -f 0.0 -q 3 > %s/%s.mgc" %
                      (bin, sp_dir, fn, bin, bin, alpha, mcsize, nFFTHalf, sp_dir, fn))

            # convert bapd to bap
            os.system("%s/x2x +df %s/%s.raw.bapd > %s/%s.bap" % (bin, bapd_dir, fn, bapd_dir, fn))

def synthesis(args, suf):
    f0_dir, sp_dir, bapd_dir = get_dir(args.dr)
    nFFTHalf, alpha, bap_dim = get_config(args.sr)
    re_wav = os.path.join(args.dr, "syn_wav_%s" % suf)
    if(os.path.exists(re_wav)):
        shutil.rmtree(re_wav)
    os.makedirs(re_wav)

    f0_files = glob.glob("%s/*.%s.f0" % (f0_dir,suf))
    print('%d files found' % len(f0_files))
    for f0_file in f0_files:
        #print('syn for %s' % f0_file)
        fn = os.path.basename(f0_file).split(".")[0]
        os.system("%s/synth %d %d %s %s/%s.%s.sp %s/%s.%s.bapd %s/%s.resyn.wav" %
                  (bin, nFFTHalf, args.sr, f0_file, sp_dir, fn, suf, bapd_dir, fn, suf, re_wav, fn))

def postprocess(args, mcsize):
    f0_dir, sp_dir, bapd_dir = get_dir(args.dr)
    nFFTHalf, alpha, bap_dim = get_config(args.sr)

    lf0_files = glob.glob("%s/*.lf0" % f0_dir)
    for lf0_file in lf0_files:
        fn = os.path.basename(lf0_file).split(".")[0]

        # convert lf0 back to f0
        os.system("%s/sopr -magic -1.0E+10 -EXP -MAGIC 0.0 %s/%s.lf0 | %s/x2x +fa > %s/%s.resyn.f0a" %
                  (bin, f0_dir, fn, bin, f0_dir, fn))
        os.system("%s/x2x +ad %s/%s.resyn.f0a > %s/%s.resyn.f0" % (bin, f0_dir, fn, f0_dir, fn))

        # convert mgc back to sp
        os.system("%s/mgc2sp -a %f -g 0 -m %d -l %d -o 2 %s/%s.mgc | %s/sopr -d 32768.0 -P | %s/x2x +fd > %s/%s.resyn.sp" %
                  (bin, alpha, mcsize, nFFTHalf, sp_dir, fn, bin, bin, sp_dir, fn))

        # convert bap back to bapd
        os.system("%s/x2x +fd %s/%s.bap > %s/%s.resyn.bapd" % (bin, bapd_dir, fn, bapd_dir, fn))


def main():
    arp = ARP(description="a demo")
    arp.add_argument("dr", help = "data root dir")
    arp.add_argument("sr", type=int, help = "sampling rate")
    arp.add_argument("--stage", dest="stage", default=0, help = "stage to run")

    args = arp.parse_args()

    mcsize=59

    stage = int(args.stage)
    if(stage <= 0):
        print("analyse...")
        analyse(args, mcsize)

    if(stage <= 1):
        print("synthesis 1...")
        synthesis(args, "raw")

    if(stage <= 2):
        print("post process...")
        postprocess(args, mcsize)

    if(stage <= 3):
        print('synthesis 2...')
        synthesis(args, "resyn")


if __name__ == "__main__":
    main()

