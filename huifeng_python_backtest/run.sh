export LD_LIBRARY_PATH=/home/ubuntu/apple/build/lib:/home/ubuntu/apple/thirdParty/lib:/home/ubuntu/huifeng/python_backtest
export CFFEX_DATA_ROOT=/home/ubuntu/huifeng/data/cffex
echo "***********************************************"
echo PLEASE READ RUN.SH AND PROPERLY SET LD_LIBRARY_PATH AND CFFEX_DATA_ROOT
echo YOU CAN SPECIFY DATE AND TICKER
echo SUCH AS: ./run.sh 20200413 IF2004
echo IF YOU LEFT IT BLANK IT USES HARD-CODED SYMBOLS
echo "************************************************"
read -n 1 -r -s -p $'Press enter to continue, or ctrl C to exit\n'
python3 start.py $1 $2 > log.txt
