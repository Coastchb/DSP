# -*- coding:utf-8 -*- 
# @Time		:2019/2/1 5:10 PM
# @Author	:Coast Cao
import librosa
import soundfile as sf
from argparse import ArgumentParser as ARP
import glob
import os

def trim_wav(filepath, args):
    wav_raw, fs = sf.read(filepath)
    wav_trim = librosa.effects.trim(wav_raw, top_db= args.trim_top_db,
                                    frame_length=args.trim_fft_size, hop_length=args.trim_hop_size)[0]
    filename = os.path.basename(filepath)
    sf.write(os.path.join(args.td, filename), wav_trim, fs)

def main():
    arp = ARP(description="trim wav")
    arp.add_argument("sd", help="source wav directory")
    arp.add_argument("td", help="target wav directory")
    arp.add_argument("--db", dest="trim_top_db", type=int, default=60)
    arp.add_argument("--fft", dest="trim_fft_size", type=int, default=512)
    arp.add_argument("--hop", dest="trim_hop_size", type=int, default= 128)
    args = arp.parse_args()

    if(not os.path.exists(args.td)):
        os.makedirs(args.td)

    wavfiles = glob.glob(os.path.join(args.sd, "*.wav"))
    wavfiles = wavfiles[:10]

    for wavfile in wavfiles:
        trim_wav(wavfile, args)



if __name__ == '__main__':
   main()
