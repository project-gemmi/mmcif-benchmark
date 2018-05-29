for n in $(seq 10); do
  /usr/bin/time --format "elapsed: %e s \t max mem: %M kb" "$1" "$2"
done
