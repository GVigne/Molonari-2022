echo 'Running all unittest'
for f in test*.py ; do
    echo 'executing' $f
    python3 $f
    done
