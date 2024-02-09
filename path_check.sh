# Make sure you are at the 

if [ $PYTHONPATH == "C:\\" ]; then
    echo 'Your PYTHONPATH is not configured yet. Configuring...'
    export PYTHONPATH="$PWD";echo $PYTHONPATH
    echo 'Your PYTHONPATH is now properly configured!'
else
    echo $PYTHONPATH
    echo 'Your PYTHONPATH is now properly configured!'
fi