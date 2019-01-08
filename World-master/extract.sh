SPTK_BIN=build
WORLD_BIN=build

if [ $# != 3 ];then
  echo "Usage:$0 wav_dir fs stage"
  exit 1
fi

wav_dir=$1
fs=$2
stage=$3


f0_dir=data/f0
lf0_dir=data/lf0
sp_dir=data/sp
mgc_dir=data/mgc
bapd_dir=data/bapd
bap_dir=data/bap
raw_syn_wav=data/syn_wav

if [ "$fs" -eq 16000 ]
then
nFFTHalf=1024
alpha=0.58
bap_dim=1
fi

if [ "$fs" -eq 22050 ]
then
nFFTHalf=1024
alpha=0.65
bap_dim=2
fi

if [ "$fs" -eq 44100 ]
then
nFFTHalf=2048
alpha=0.76
bap_dim=5
fi

if [ "$fs" -eq 48000 ]
then
nFFTHalf=2048
alpha=0.77
bap_dim=5
fi

#bap order depends on sampling freq.
mcsize=59

if [ $stage -le 1 ];then
  [ ! -d $wav_dir ] && echo "$wav_dir doesn't exists!" && exit 1
  for d in $f0_dir $lf0_dir $sp_dir $mgc_dir $bapd_dir $bap_dir $raw_syn_wav; do
    [ ! -d $d ] && mkdir -p $d
  done

  ### extract acoustic feature and their delta, delta-delta ###
  for wav_file in `ls $wav_dir`;do
    base=${wav_file%.*}

    ### extract f0, sp, ap ###
    $WORLD_BIN/analysis $wav_dir/$wav_file $f0_dir/${base}.f0 $sp_dir/${base}.sp $bapd_dir/${base}.bapd || exit 1

    ### copy synthesis with the raw(without converting) acoustic features
    $WORLD_BIN/synth $nFFTHalf $fs $f0_dir/${base}.f0 $sp_dir/${base}.sp $bapd_dir/${base}.bapd ${raw_syn_wav}/${base}.resyn.wav

    ### convert f0 to lf0 ###
    $SPTK_BIN/x2x +da $f0_dir/${base}.f0 > $f0_dir/${base}.f0a || exit 1
    $SPTK_BIN/x2x +af $f0_dir/${base}.f0a | $SPTK_BIN/sopr -magic 0.0 -LN -MAGIC -1.0E+10 > $lf0_dir/${base}.lf0_s || exit 1
    /usr/bin/perl scripts/window.pl 1 $lf0_dir/${base}.lf0_s win/lf0.win1 win/lf0.win2 win/lf0.win3 > $lf0_dir/${base}.lf0 || exit 1

    ### convert sp to mgc ###
    $SPTK_BIN/x2x +df $sp_dir/${base}.sp | $SPTK_BIN/sopr -R -m 32768.0 | $SPTK_BIN/mcep -a $alpha -m $mcsize -l $nFFTHalf -e 1.0E-8 -j 0 -f 0.0 -q 3 \
     > $mgc_dir/${base}.mgc_s || exit 1
    /usr/bin/perl scripts/window.pl $[mcsize+1] $mgc_dir/${base}.mgc_s win/mgc.win1 win/mgc.win2 win/mgc.win3 > $mgc_dir/${base}.mgc || exit 1

    ### convert bapd to bap ###
    $SPTK_BIN/x2x +df $bapd_dir/${base}.bapd > $bap_dir/${base}.bap_s || exit 1
    # Question: how to set bap_dim
    /usr/bin/perl scripts/window.pl $bap_dim $bap_dir/${base}.bap_s win/bap.win1 win/bap.win2 win/bap.win3 > $bap_dir/${base}.bap || exit 1

  done
fi

syn_f0=data/syn/f0
syn_sp=data/syn/sp
syn_bapd=data/syn/bap
syn_wav=data/syn/wav

if [ $stage -le 2 ];then
  for d in $syn_bapd $syn_f0 $syn_sp $syn_wav;do
    [ ! -d $d ] && mkdir -p $d
  done

  ### copy synthesis with extracted(and converted) static acoustic features ###
  ### it can be referred by synthesis with predicted acoustic features ###
  for lf0_file in `ls $lf0_dir`; do
    base=${lf0_file%.*}

    # convert extracted lf0 to f0
    $SPTK_BIN/sopr -magic -1.0E+10 -EXP -MAGIC 0.0 ${lf0_dir}/${base}.lf0_s | $SPTK_BIN/x2x +fa > ${syn_f0}/${base}.resyn.f0a
    $SPTK_BIN/x2x +ad ${syn_f0}/${base}.resyn.f0a > ${syn_f0}/${base}.resyn.f0

    # convert extracted mgc to sp
    $SPTK_BIN/mgc2sp -a $alpha -g 0 -m $mcsize -l $nFFTHalf -o 2 ${mgc_dir}/${base}.mgc_s | $SPTK_BIN/sopr -d 32768.0 -P | $SPTK_BIN/x2x +fd > ${syn_sp}/${base}.resyn.sp

    # convert extracted bap to bapd
    $SPTK_BIN/x2x +fd ${bap_dir}/${base}.bap_s > ${syn_bapd}/${base}.resyn.bapd

    $WORLD_BIN/synth $nFFTHalf $fs ${syn_f0}/${base}.resyn.f0 ${syn_sp}/${base}.resyn.sp ${syn_bapd}/${base}.resyn.bapd ${syn_wav}/${base}.resyn.wav
  done
fi
