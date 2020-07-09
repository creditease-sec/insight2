
python -m compileall .
git add .
git commit -am 'build..'
git push origin community
python removepy.py


