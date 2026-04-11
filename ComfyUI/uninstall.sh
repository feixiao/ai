
killall -9 ComfyUI 2>/dev/null
killall -9 python 2>/dev/null
brew uninstall comfyui
rm -rf /Applications/ComfyUI.app
rm -rf ~/Library/Application\ Support/ComfyUI
rm -rf ~/Library/Caches/ComfyUI
rm -rf ~/Library/Caches/com.comfyui.*
rm -rf ~/Library/Logs/ComfyUI
rm -f ~/Library/Preferences/com.comfyui.*
rm -rf /Users/frank/Documents/ComfyUI
#rm -rf /Users/frank/Documents/自媒体
echo "✅ ComfyUI 已完全卸载"