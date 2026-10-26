function wechat --description 'Launch WeChat with fcitx5 input method support'
    QT_IM_MODULE=text-input-unstable-v3 \
        XMODIFIERS=@im=fcitx \
        /opt/wechat/wechat $argv
end
