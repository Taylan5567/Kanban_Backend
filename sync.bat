@echo off
echo 🔄 Git Pull...
git pull origin main

echo 📝 Git Add...
git add .

set /p msg=✍️ Commit-Nachricht eingeben: 

echo 💾 Git Commit...
git commit -m "%msg%"

echo 🚀 Git Push...
git push origin main

pause
