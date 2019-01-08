SPTK_BIN=build
WORLD_BIN=build

if [ $# != 2 ];then
  echo "Usage:$0 wav_dir fs"
  exit 1
fi

wav_dir=$1
fs=$2


f0_dir=data/f0
lf0_dir=data/lf0
sp_dir=data/sp
mgc_dir=data/mgc
bapd_dir=data/bapd
bap_dir=data/bap


[ ! -d $wav_dir ] && echo "$wav_dir doesn't exists!" && exit 1
for d in $f0_dir $lf0_dir $sp_dir $mgc_dir $bapd_dir $bap_dir; do
  [ ! -d $d ] && mkdir -p $d
done

if [ "$fs" -eq 16000 ]
then
nFFTHalf=1024
alpha=0.58
fi

if [ "$fs" -eq 22050 ]
then
nFFTHalf=1024
alpha=0.65
fi

if [ "$fs" -eq 44100 ]
then
nFFTHalf=2048
alpha=0.76
fi

if [ "$fs" -eq 48000 ]
then
nFFTHalf=2048
alpha=0.77
fi

#bap order depends on sampling freq.
mcsize=59

for wav_file in `ls $wav_dir`;do
  base=${wav_file%.*}

  ### extract f0, sp, ap ###
  $WORLD_BIN/analysis $wav_dir/$wav_file $f0_dir/${base}.f0 $sp_dir/${base}.sp $bapd_dir/${base}.bapd || exit 1

  ### convert f0 to lf0 ###
  $SPTK_BIN/x2x +da $f0_dir/${base}.f0 > $f0_dir/${base}.f0a || exit 1
  $SPTK_BIN/x2x +af $f0_dir/${base}.f0a | $SPTK_BIN/sopr -magic 0.0 -LN -MAGIC -1.0E+10 > $lf0_dir/${base}.lf0 || exit 1
  echo 'lf0 ok'

  ### convert sp to mgc ###
  $SPTK_BIN/x2x +df $sp_dir/${base}.sp | $SPTK_BIN/sopr -R -m 32768.0 | $SPTK_BIN/mcep -a $alpha -m $mcsize -l $nFFTHalf -e 1.0E-8 -j 0 -f 0.0 -q 3 \
   > $mgc_dir/${base}.mgc || exit 1
  echo 'mgc ok'

  ### convert bapd to bap ###
  $SPTK_BIN/x2x +df $bapd_dir/${base}.bapd > $bap_dir/${base}.bap || exit 1
  echo 'bap ok'
done