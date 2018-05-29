prog="$1"
for cif in *.cif *.ent; do
  echo $prog - $cif
  ./run-one.sh $prog $cif
done
