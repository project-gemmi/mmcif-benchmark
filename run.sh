prog="$1"
for cif in 4fxz.cif 1cjb.cif 3j3q.cif r4v9psf.ent components.cif; do
  echo $prog - $cif
  ./run-one.sh $prog $cif
done
