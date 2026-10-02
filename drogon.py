from flask import Flask, request, jsonify, render_template_string, send_file
import requests
import re
import os
import json
import threading
import secrets
import hmac
import time
import hashlib
import gzip
import io
import base64
import zipfile

app = Flask(__name__)

# HTML from user (with minor adjustments for Flask)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=1.0, user-scalable=yes">
<title>MODYXBIO | محرر البايو - الشرق الأوسط ME</title>
<meta name="theme-color" content="var(--a)" id="themeColorMeta">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon-192.png">
<link rel="icon" type="image/png" href="/icon-192.png">
<meta property="og:type" content="website">
<meta property="og:title" content="MODYXBIO | محرر البايو">
<meta property="og:description" content="بوت وموقع تغيير البايو لفري فاير: سريع، آمن، ومجاني.">
<meta property="og:image" content="__ORIGIN__/logo.png">
<meta name="twitter:card" content="summary">
<meta name="mobile-web-app-capable" content="yes">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #000; color: white; font-family: 'Segoe UI', monospace; overflow-x: hidden; }
canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }
.container { position: relative; z-index: 1; max-width: 500px; margin: 0 auto; padding: 16px 16px 30px; }
h1 { text-align: center; color: var(--a); text-shadow: 0 0 12px var(--a); font-size: 1.8rem; margin: 10px 0 5px; }
.subtitle { text-align: center; color: #888; font-size: 0.9rem; margin-bottom: 15px; }
.card { background: rgba(20, 25, 40, 0.65); backdrop-filter: blur(12px); border-radius: 28px; padding: 18px; margin: 16px 0; border: 1px solid color-mix(in srgb, var(--a) 25%, transparent); }
textarea { width: 100%; height: 130px; border-radius: 20px; background: #0a0a0e; border: 1px solid var(--a); color: white; padding: 14px; font-size: 15px; resize: vertical; font-family: monospace; }
.preview { margin-top: 12px; padding: 12px; background: #0a0a0e; border-radius: 20px; border: 1px solid var(--a); min-height: 65px; font-size: 15px; word-wrap: break-word; }
button, .format-btn { background: linear-gradient(90deg, var(--a), var(--a2)); border: none; border-radius: 40px; padding: 8px 14px; margin: 5px 4px; font-weight: bold; color: black; cursor: pointer; font-size: 14px; }
.colors-ribbon { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 12px; }
.c-dot { height: 36px; border-radius: 12px; cursor: pointer; border: 1px solid rgba(255,255,255,0.3); }
input, select { width: 100%; padding: 12px; margin-top: 8px; border-radius: 60px; background: #0a0a0e; border: 1px solid #333; color: white; font-size: 14px; }
#overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(20px); z-index: 1000; display: flex; flex-direction: column; justify-content: center; align-items: center; opacity: 0; visibility: hidden; transition: 0.2s; }
#overlay.active { opacity: 1; visibility: visible; }
.res-icon { font-size: 70px; margin-bottom: 16px; }
.res-title { font-size: 28px; font-weight: bold; }
.res-body { text-align: center; padding: 20px; max-width: 85%; word-break: break-word; }
.success .res-icon { color: var(--a); }
.error .res-icon { color: #ff5555; }
.links a { color:var(--a); margin:0 8px; text-decoration:none; }
.api-badge { display: inline-block; background: color-mix(in srgb, var(--a) 13%, transparent); color: var(--a); padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; border: 1px solid color-mix(in srgb, var(--a) 33%, transparent); }

/* ===== CAPTCHA STYLES ===== */
#captchaOverlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.95);
    backdrop-filter: blur(30px);
    z-index: 2000;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    padding: 20px;
}
#captchaOverlay.hidden {
    display: none;
}
.captcha-box {
    background: rgba(20, 25, 40, 0.95);
    border-radius: 32px;
    padding: 35px 30px;
    max-width: 440px;
    width: 100%;
    border: 2px solid color-mix(in srgb, var(--a) 30%, transparent);
    box-shadow: 0 0 80px color-mix(in srgb, var(--a) 10%, transparent), inset 0 0 60px color-mix(in srgb, var(--a) 5%, transparent);
    text-align: center;
    animation: captchaPulse 2s infinite;
}
@keyframes captchaPulse {
    0% { border-color: color-mix(in srgb, var(--a) 30%, transparent); box-shadow: 0 0 80px color-mix(in srgb, var(--a) 10%, transparent); }
    50% { border-color: color-mix(in srgb, var(--a) 60%, transparent); box-shadow: 0 0 100px color-mix(in srgb, var(--a) 20%, transparent); }
    100% { border-color: color-mix(in srgb, var(--a) 30%, transparent); box-shadow: 0 0 80px color-mix(in srgb, var(--a) 10%, transparent); }
}
.captcha-box .robot-icon {
    font-size: 64px;
    margin-bottom: 5px;
    animation: robotFloat 3s ease-in-out infinite;
}
@keyframes robotFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
.captcha-box h2 {
    color: var(--a);
    font-size: 1.5rem;
    margin-bottom: 6px;
    text-shadow: 0 0 20px color-mix(in srgb, var(--a) 30%, transparent);
}
.captcha-box .sub-text {
    color: #aaa;
    font-size: 0.85rem;
    margin-bottom: 20px;
    line-height: 1.5;
}
.captcha-slider-container {
    background: #0a0a0e;
    border-radius: 60px;
    padding: 4px;
    border: 2px solid #333;
    position: relative;
    margin: 15px 0;
    display: flex;
    align-items: center;
    user-select: none;
    -webkit-user-select: none;
    touch-action: none;
    height: 60px;
    transition: border-color 0.3s;
}
.captcha-slider-container:hover,
.captcha-slider-container.active {
    border-color: var(--a);
}
.captcha-slider-track {
    flex: 1;
    height: 100%;
    border-radius: 60px;
    background: #1a1a2e;
    position: relative;
    overflow: hidden;
}
.captcha-slider-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, var(--a), var(--a2));
    border-radius: 60px;
    transition: width 0.05s linear;
    position: absolute;
    left: 0;
    top: 0;
}
.captcha-slider-thumb {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--a), var(--a2));
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    left: 2px;
    box-shadow: 0 0 30px color-mix(in srgb, var(--a) 40%, transparent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: #000;
    transition: left 0.05s linear, background 0.3s;
    z-index: 2;
    cursor: grab;
    touch-action: none;
}
.captcha-slider-thumb:active {
    cursor: grabbing;
}
.captcha-slider-thumb i {
    pointer-events: none;
}
.captcha-status {
    margin: 14px 0 8px;
    font-size: 0.95rem;
    min-height: 30px;
    font-weight: 500;
}
.captcha-status.verified {
    color: var(--a);
}
.captcha-status.failed {
    color: #ff5555;
}
.captcha-refresh {
    background: transparent;
    border: 1px solid #444;
    color: #aaa;
    padding: 8px 20px;
    border-radius: 25px;
    font-size: 0.8rem;
    cursor: pointer;
    margin-top: 5px;
    transition: all 0.3s;
}
.captcha-refresh:hover {
    border-color: var(--a);
    color: var(--a);
    background: color-mix(in srgb, var(--a) 5%, transparent);
}
.captcha-progress-text {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    z-index: 1;
    font-weight: bold;
    letter-spacing: 0.5px;
    pointer-events: none;
    transition: color 0.3s;
}
.captcha-footer {
    margin-top: 15px;
    font-size: 0.7rem;
    color: #444;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
.captcha-footer i {
    color: var(--a);
}
.captcha-lock {
    margin-bottom: 10px;
    color: var(--a);
    font-size: 14px;
}
.captcha-lock i {
    margin-right: 6px;
}

/* Mobile touch optimization */
@media (max-width: 480px) {
    .captcha-slider-container {
        height: 56px;
    }
    .captcha-slider-thumb {
        width: 48px;
        height: 48px;
        font-size: 18px;
    }
    .captcha-box {
        padding: 25px 20px;
    }
}

/* ===== MODYXBIO EXTRAS ===== */
:root{--a:#00ffc3;--a2:#0099ff;--b1:#050510;--b2:#0b1a2e}
body{font-family:'Cairo','Segoe UI',sans-serif!important;background:linear-gradient(135deg,var(--b1),var(--b2),var(--b1))!important;background-size:300% 300%!important;animation:bgFlow 14s ease infinite}
@keyframes bgFlow{0%{background-position:0 50%}50%{background-position:100% 50%}100%{background-position:0 50%}}
.captcha-slider-container{direction:ltr}
h1{background:linear-gradient(90deg,var(--a),#fff,var(--a2),var(--a));background-size:300% 100%;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:shine 5s linear infinite;font-weight:900;font-size:2.3rem;letter-spacing:2px;filter:drop-shadow(0 0 12px var(--a))}
@keyframes shine{to{background-position:300% 0}}
.card{animation:rise .7s both;transition:transform .25s,box-shadow .3s;box-shadow:0 0 18px color-mix(in srgb,var(--a) 15%,transparent)}
.card:nth-of-type(2){animation-delay:.1s}.card:nth-of-type(3){animation-delay:.2s}.card:nth-of-type(4){animation-delay:.3s}
.card:hover{box-shadow:0 0 34px color-mix(in srgb,var(--a) 40%,transparent)}
@keyframes rise{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
button,.format-btn{font-family:inherit;position:relative;overflow:hidden;transition:transform .2s,box-shadow .2s}
button:hover,.format-btn:hover{transform:translateY(-2px) scale(1.04);box-shadow:0 6px 20px color-mix(in srgb,var(--a) 50%,transparent)}
button::after{content:"";position:absolute;top:0;left:-120%;width:60%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.55),transparent);transform:skewX(-20deg);animation:sweep 3.5s infinite}
@keyframes sweep{to{left:160%}}
textarea,input,select{font-family:inherit;transition:box-shadow .25s}textarea:focus,input:focus,select:focus{outline:none;box-shadow:0 0 16px var(--a)}
.links{display:flex;justify-content:center;gap:10px;flex-wrap:wrap}
.links a{background:rgba(0,0,0,.5);padding:8px 16px;border-radius:30px;border:1px solid var(--a);transition:.2s}.links a:hover{background:var(--a);color:#000!important;transform:translateY(-3px)}
.colors-ribbon{grid-template-columns:repeat(8,1fr)}
.c-dot{transition:transform .15s}.c-dot:hover{transform:scale(1.25);z-index:2;box-shadow:0 0 12px #fff}
.themes{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:8px}
.th{height:40px;border-radius:12px;cursor:pointer;border:2px solid rgba(255,255,255,.35);transition:.2s}.th:hover,.th.on{transform:scale(1.12);border-color:#fff;box-shadow:0 0 14px #fff}
.row{display:flex;gap:10px;align-items:center;margin-top:10px}.row label{flex:1;font-size:.85rem;color:#ddd}
input[type=color]{width:58px;height:40px;padding:2px;margin:0;border-radius:12px;cursor:pointer}
.social{display:flex;justify-content:center;gap:14px;margin:12px 0;flex-wrap:wrap}
.social a{width:52px;height:52px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;color:#fff;text-decoration:none;transition:.25s;animation:float 3s ease-in-out infinite}
.social a:nth-child(2){animation-delay:.4s}.social a:nth-child(3){animation-delay:.8s}.social a:hover{transform:scale(1.2) rotate(8deg)}
@keyframes float{50%{transform:translateY(-6px)}}
.tg{background:#229ED9;box-shadow:0 0 18px #229ED9}.wa{background:#25D366;box-shadow:0 0 18px #25D366}.tt{background:#000;border:2px solid #fe2c55;box-shadow:-3px -3px 0 #25f4ee,3px 3px 0 #fe2c55}
.stamp{width:140px;height:140px;margin:18px auto 4px;border:4px double #e63946;border-radius:50%;color:#e63946;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-12deg);font-weight:900;text-shadow:0 0 8px rgba(230,57,70,.5);box-shadow:inset 0 0 0 3px rgba(230,57,70,.35),0 0 22px rgba(230,57,70,.3);background:rgba(230,57,70,.07);animation:stampIn 1s both}
.stamp b{font-size:1.15rem;letter-spacing:1px}.stamp small{font-size:.62rem;letter-spacing:3px}
@keyframes stampIn{0%{transform:rotate(-40deg) scale(3);opacity:0}70%{transform:rotate(-12deg) scale(.9)}100%{transform:rotate(-12deg) scale(1);opacity:.9}}
.foot{text-align:center;color:#aaa;font-size:.75rem;margin-top:12px}
#musicBtn{position:fixed;bottom:14px;left:14px;z-index:60;width:46px;height:46px;border-radius:50%;padding:0;font-size:18px;margin:0}
#viz{position:fixed;bottom:14px;left:68px;z-index:60;width:120px;height:46px;pointer-events:none}
#ttFloat{position:fixed;bottom:14px;right:14px;z-index:60;width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:21px;text-decoration:none;background:#000;border:2px solid #fe2c55;box-shadow:-3px -3px 0 #25f4ee,3px 3px 0 #fe2c55;animation:float 2.5s infinite}
.orb{position:fixed;border-radius:50%;filter:blur(60px);opacity:.28;z-index:0;pointer-events:none;background:var(--a);animation:drift 18s ease-in-out infinite alternate}
@keyframes drift{to{transform:translate(60vw,40vh) scale(1.5)}}
.tr{position:fixed;width:9px;height:9px;border-radius:50%;background:var(--a);pointer-events:none;z-index:4000;box-shadow:0 0 12px var(--a)}
.cf{position:fixed;top:-10px;width:10px;height:14px;z-index:5000;pointer-events:none}
#welcome{z-index:3000}
.ttlogo{font-size:64px;color:#fff;text-shadow:-3px -3px 0 #25f4ee,3px 3px 0 #fe2c55;animation:float 2s infinite}
.big{display:block;width:100%;padding:13px;margin:10px 0;font-size:1rem;border-radius:40px}
a.big{text-decoration:none;font-weight:700;text-align:center;background:#fe2c55;color:#fff}

/* ===== TOKYO NEON ===== */
#welcome{z-index:3000}
#matrix{opacity:.25}
#scene{position:fixed;inset:0;z-index:-1;pointer-events:none;background:linear-gradient(180deg,transparent 40%,color-mix(in srgb,var(--a2) 20%,transparent))}
#scene svg{width:100%;height:100%;display:block}
#rain{position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none}
.neon{filter:drop-shadow(0 0 3px currentColor) drop-shadow(0 0 12px currentColor) drop-shadow(0 0 26px currentColor);animation:flick 6s infinite}
.neon.n2{animation-delay:-2s;animation-duration:7s}.neon.n3{animation-delay:-4s;animation-duration:5s}
@keyframes flick{0%,17%,19%,60%,62%,100%{opacity:1}18%,61%{opacity:.3}}
.win{animation:winb 7s infinite}@keyframes winb{0%,45%,100%{opacity:.9}50%{opacity:.15}}
.devbox{margin:12px auto;max-width:420px;padding:12px;border:2px dashed var(--a);border-radius:16px;background:rgba(0,0,0,.45);font-weight:700;line-height:2;word-break:break-word;text-align:center}
.devbox span{color:var(--a)}
.chips{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0}
.item{background:rgba(0,0,0,.45);border:1px solid color-mix(in srgb,var(--a) 35%,transparent);border-radius:14px;padding:10px;margin-top:8px;font-size:.88rem;word-break:break-word}
.item small{color:#aaa;display:block;margin-bottom:4px}
.item button{padding:5px 12px;font-size:12px;margin:6px 3px 0 0}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center}
.stats div{background:rgba(0,0,0,.45);border:1px solid color-mix(in srgb,var(--a) 35%,transparent);border-radius:16px;padding:12px 4px}
.stats b{display:block;font-size:1.5rem;color:var(--a);text-shadow:0 0 10px var(--a)}.stats small{font-size:.72rem;color:#ccc}
#ticker{position:fixed;top:0;left:0;right:0;height:34px;z-index:100;overflow:hidden;direction:ltr;background:rgba(0,0,0,.78);border-bottom:2px solid var(--a);box-shadow:0 0 16px color-mix(in srgb,var(--a) 50%,transparent)}
#tk{display:inline-flex;white-space:nowrap;align-items:center;height:100%;animation:tkm 45s linear infinite}
#ticker:hover #tk{animation-play-state:paused}
#tk a{color:#fff;text-decoration:none;font-size:.85rem;font-weight:700;padding:0 14px}#tk span{color:var(--a)}
@keyframes tkm{to{transform:translateX(-50%)}}
.container{padding-top:50px!important}
.toast{position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:var(--a);color:#000;font-weight:700;padding:10px 20px;border-radius:30px;z-index:9500;box-shadow:0 0 20px var(--a)}
#loader{position:fixed;inset:0;z-index:9000;background:radial-gradient(circle at 50% 40%,#1b0a40,#02020a);display:flex;flex-direction:column;align-items:center;justify-content:center;transition:opacity .7s}
#loader.off{opacity:0;pointer-events:none}
.lg{font-size:2.6rem;font-weight:900;color:var(--a);text-shadow:0 0 12px var(--a),0 0 36px var(--a2);animation:flick 3s infinite}
.lbar{width:min(300px,80%);height:10px;border-radius:10px;background:rgba(255,255,255,.1);margin:22px 0 10px;overflow:hidden;border:1px solid var(--a)}
#lfill{height:100%;width:0;background:linear-gradient(90deg,var(--a),var(--a2));box-shadow:0 0 14px var(--a);transition:width .12s}
#lpct{font-weight:900;font-size:1.3rem}#ltxt{color:#bbb;font-size:.85rem;margin-top:4px}

/* ===== v5 ===== */
#langBtn{position:fixed;top:42px;right:10px;z-index:90;padding:6px 14px;font-size:12px;margin:0}
.modal{position:fixed;inset:0;z-index:8000;background:rgba(0,0,0,.9);display:none;align-items:flex-start;justify-content:center;padding:16px;overflow:auto}
.modal.on{display:flex}
.mbox{background:rgba(15,20,35,.97);border:2px solid var(--a);border-radius:22px;padding:18px;max-width:520px;width:100%;margin:30px 0;box-shadow:0 0 40px color-mix(in srgb,var(--a) 35%,transparent)}
.mbox h3{margin-bottom:8px;color:var(--a)}
#stars{text-align:center;direction:ltr}
#stars span{font-size:2.4rem;cursor:pointer;color:#555;transition:.15s;padding:0 3px}
#stars span.on{color:#ffd23f;text-shadow:0 0 14px #ffd23f}
.sb{display:inline-flex;align-items:center;gap:6px;padding:9px 14px;border-radius:30px;color:#fff;text-decoration:none;font-weight:700;font-size:.85rem;border:none;cursor:pointer;font-family:inherit}
.item button.liked{background:#ff4d6d;color:#fff}
input[type=checkbox]{width:auto;margin:0 0 0 8px;accent-color:var(--a);transform:scale(1.3);vertical-align:middle}
.pub{display:block;margin-top:14px;font-size:.88rem;line-height:1.7}
.tabs{display:flex;gap:6px;margin-bottom:6px}.tabs button{flex:1;margin:0}.tabs button.off{opacity:.45}

/* ===== v6 DESIGN ===== */
@property --ang{syntax:'<angle>';initial-value:0deg;inherits:false}
@keyframes ang{to{--ang:360deg}}
@keyframes blink{50%{opacity:0}}
@keyframes spin2{to{transform:rotate(360deg)}}
@keyframes drive{from{transform:translateX(-160px)}to{transform:translateX(1160px)}}
@keyframes mpulse{0%,100%{box-shadow:0 0 0 0 color-mix(in srgb,var(--a) 70%,transparent)}50%{box-shadow:0 0 0 12px transparent}}
html{scroll-behavior:smooth}
::selection{background:var(--a);color:#000}
::-webkit-scrollbar{width:8px}::-webkit-scrollbar-track{background:#05050f}::-webkit-scrollbar-thumb{background:linear-gradient(var(--a),var(--a2));border-radius:8px}
::placeholder{color:#8a8fb0}
body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.6))}
#scene{transition:transform .25s ease-out;will-change:transform}
.car{animation:drive linear infinite}
.container{padding-bottom:100px!important}
h1{font-size:clamp(2.3rem,10vw,3.6rem)!important;margin-bottom:0!important}
.hero-line{height:3px;width:150px;margin:6px auto 10px;border-radius:3px;background:linear-gradient(90deg,transparent,var(--a),var(--a2),transparent);box-shadow:0 0 16px var(--a)}
.tw{text-align:center;min-height:30px;font-weight:700;font-size:1.02rem;color:#e8ecff;margin-bottom:8px}
.tw::after{content:"|";margin-inline-start:3px;color:var(--a);animation:blink 1s infinite}
.card{border:2px solid transparent!important;border-radius:24px!important;background:linear-gradient(rgba(10,12,28,.78),rgba(10,12,28,.78)) padding-box,conic-gradient(from var(--ang),var(--a),var(--a2),transparent 38%,var(--a)) border-box!important;animation:ang 7s linear infinite!important;scroll-margin-top:52px;box-shadow:0 10px 40px rgba(0,0,0,.45),0 0 26px color-mix(in srgb,var(--a) 14%,transparent)}
.card h3{display:flex;align-items:center;gap:8px;font-weight:900;font-size:1.1rem;padding-bottom:10px;margin-bottom:12px;border-bottom:1px solid rgba(255,255,255,.1)}
.rv{opacity:0;transform:translateY(36px);transition:opacity .7s,transform .7s}
.rv.in{opacity:1;transform:none;transition:opacity .7s,transform .2s}
button:active,.format-btn:active{transform:scale(.94)!important}
textarea,input,select{border-radius:16px!important;background:rgba(0,0,0,.55)!important}
.preview{font-size:1.1rem;text-align:center;min-height:76px;display:flex;align-items:center;justify-content:center;border-radius:18px}
.captcha-box{border-radius:30px;box-shadow:0 0 70px color-mix(in srgb,var(--a) 28%,transparent)}
#loader::before{content:"";position:absolute;left:50%;top:50%;width:250px;height:250px;margin:-135px 0 0 -125px;border-radius:50%;border:3px solid transparent;border-top-color:var(--a);border-bottom-color:var(--a2);animation:spin2 1.3s linear infinite;filter:drop-shadow(0 0 10px var(--a))}
#musicBtn.playing{animation:mpulse 1.3s infinite}
#viz{bottom:70px!important;left:14px!important}
#nav{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);z-index:70;display:flex;gap:4px;padding:6px;border-radius:40px;background:rgba(8,8,22,.85);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid color-mix(in srgb,var(--a) 55%,transparent);box-shadow:0 0 26px color-mix(in srgb,var(--a) 32%,transparent)}
#nav button{width:44px;height:44px;border-radius:50%;padding:0;margin:0;font-size:19px;background:transparent;color:#fff;box-shadow:none}
#nav button::after{display:none}
#nav button.on,#nav button:hover{background:linear-gradient(135deg,var(--a),var(--a2));transform:scale(1.1)}

/* ===== v7 REAL SITE ===== */
.container{padding-top:100px!important}
#nav2{position:fixed;top:34px;left:0;right:0;height:52px;z-index:95;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:0 14px;background:rgba(6,6,18,.74);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid rgba(255,255,255,.08)}
.logo{font-weight:900;font-size:1.15rem;color:var(--a);text-shadow:0 0 12px var(--a);text-decoration:none;white-space:nowrap}
#nav2 .lk{display:none;gap:2px}
#nav2 .lk a{color:#dfe3ff;text-decoration:none;font-size:.86rem;font-weight:700;padding:8px 12px;border-radius:20px;transition:.2s}
#nav2 .lk a:hover{background:color-mix(in srgb,var(--a) 20%,transparent);color:var(--a)}
#nav2 #langBtn{position:static;margin:0}
.card,.sec{scroll-margin-top:96px}
.hero{text-align:center;padding:26px 0 8px}
.eyebrow{display:inline-block;padding:5px 16px;border-radius:30px;border:1px solid var(--a);background:color-mix(in srgb,var(--a) 12%,transparent);font-size:.8rem;font-weight:700;margin-bottom:10px}
.lead{max-width:580px;margin:0 auto 18px;color:#c5c9e8;line-height:1.9;font-size:.95rem}
.cta{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.btn-p,.btn-g{padding:13px 26px;border-radius:40px;font-weight:900;text-decoration:none;transition:.2s;font-size:.95rem}
.btn-p{background:linear-gradient(90deg,var(--a),var(--a2));color:#000;box-shadow:0 0 24px color-mix(in srgb,var(--a) 50%,transparent)}
.btn-g{border:2px solid var(--a);color:#fff;background:rgba(0,0,0,.35)}
.btn-p:hover,.btn-g:hover{transform:translateY(-3px)}
.hstats{display:flex;justify-content:center;gap:10px;margin:22px 0 8px}
.hstats div{min-width:92px;padding:10px 12px;border-radius:16px;background:rgba(10,12,28,.72);border:1px solid rgba(255,255,255,.1)}
.hstats b{display:block;font-size:1.3rem;color:var(--a);text-shadow:0 0 10px var(--a)}.hstats small{font-size:.72rem;color:#b9bedc}
.by{font-size:.78rem;color:#9aa0c4;margin-top:8px}
.cols{display:block}
.sec{margin:46px 0 10px}
.sec h2{text-align:center;font-size:1.6rem;font-weight:900}
.sec h2::after{content:"";display:block;width:70px;height:3px;margin:8px auto 18px;background:linear-gradient(90deg,var(--a),var(--a2));border-radius:3px;box-shadow:0 0 12px var(--a)}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}
.feat{background:rgba(10,12,28,.74);border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:20px 16px;text-align:center;transition:.25s;backdrop-filter:blur(10px)}
.feat:hover{transform:translateY(-6px);border-color:var(--a);box-shadow:0 12px 34px color-mix(in srgb,var(--a) 25%,transparent)}
.feat i{font-style:normal;font-size:2rem;display:block;margin-bottom:6px}.feat b{display:block;margin-bottom:4px}.feat p{font-size:.85rem;color:#b9bedc;line-height:1.7}
.num{display:inline-flex;width:42px;height:42px;border-radius:50%;align-items:center;justify-content:center;font-weight:900;font-size:1.2rem;color:#000;background:linear-gradient(135deg,var(--a),var(--a2));margin-bottom:8px;box-shadow:0 0 16px var(--a)}
.faq details{background:rgba(10,12,28,.74);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:14px 16px;margin-top:10px;transition:.2s}
.faq details[open]{border-color:var(--a)}
.faq summary{cursor:pointer;font-weight:700;list-style:none;display:flex;justify-content:space-between;align-items:center}
.faq summary::-webkit-details-marker{display:none}.faq summary::after{content:"+";color:var(--a);font-size:1.4rem}.faq details[open] summary::after{content:"−"}
.faq p{margin-top:10px;color:#c5c9e8;line-height:1.8;font-size:.9rem}
.ft2{margin-top:40px;border-top:1px solid color-mix(in srgb,var(--a) 40%,transparent);padding:28px 0 10px}
.fgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:20px}
.fgrid b{display:block;margin-bottom:8px;color:var(--a)}.fgrid a{display:block;color:#ccd;text-decoration:none;font-size:.88rem;padding:3px 0}.fgrid a:hover{color:var(--a)}
.copy{text-align:center;color:#8a8fb0;font-size:.75rem;margin-top:22px;line-height:2}
@media(min-width:800px){ #nav2 .lk{display:flex}#nav{display:none}.hero{padding-top:50px}}
@media(min-width:900px){.container{max-width:1120px!important}.cols{display:grid;grid-template-columns:1.1fr 1fr;gap:20px;align-items:start}.cols .card{margin:0 0 20px!important}#secCt{max-width:700px;margin-inline:auto}}

/* ===== v8 COLOR EXPLOSION ===== */
#aur{position:fixed;left:-25%;right:-25%;top:-10%;height:90vh;z-index:-1;pointer-events:none;background:conic-gradient(from var(--ang) at 50% 110%,var(--a),var(--a2),transparent 28%,#ffd23f 48%,transparent 62%,var(--a));filter:blur(90px);opacity:.34;animation:ang 22s linear infinite}
#ticker::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,var(--a),#ffd23f,#ff2bd6,var(--a2),var(--a));background-size:300% 100%;animation:shine 6s linear infinite}
h1{background:linear-gradient(90deg,var(--a),#ffffff,var(--a2),#ffd23f,var(--a))!important;background-size:400% 100%!important;-webkit-background-clip:text!important;background-clip:text!important;-webkit-text-fill-color:transparent;animation:shine 7s linear infinite!important}
.hero{position:relative}
.hero::before{content:"";position:absolute;left:50%;top:40%;width:min(520px,90vw);height:300px;transform:translate(-50%,-50%);background:radial-gradient(closest-side,color-mix(in srgb,var(--a) 28%,transparent),color-mix(in srgb,var(--a2) 14%,transparent) 60%,transparent);filter:blur(20px);z-index:-1;pointer-events:none}
.sec h2{background:linear-gradient(90deg,var(--a),#fff,var(--a2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.card{--c1:var(--a);--c2:var(--a2);--tc:#000;position:relative}
.cols .card:nth-child(5n+2){--c1:var(--a2);--c2:#ffd23f}
.cols .card:nth-child(5n+3){--c1:#39ff14;--c2:var(--a)}
.cols .card:nth-child(5n+4){--c1:#ff2bd6;--c2:#7b2ff7;--tc:#fff}
.cols .card:nth-child(5n){--c1:#ffb300;--c2:var(--a2)}
.card{background:linear-gradient(rgba(10,12,28,.8),rgba(10,12,28,.8)) padding-box,conic-gradient(from var(--ang),var(--c1),var(--c2),transparent 38%,var(--c1)) border-box!important;box-shadow:0 10px 40px rgba(0,0,0,.45),0 0 28px color-mix(in srgb,var(--c1) 16%,transparent)!important}
.card h3{color:var(--c1);text-shadow:0 0 14px color-mix(in srgb,var(--c1) 55%,transparent);border-image:linear-gradient(90deg,var(--c1),var(--c2),transparent) 1}
.card .format-btn,.card button:not(.liked){background:linear-gradient(90deg,var(--c1),var(--c2));background-size:200% 100%;color:var(--tc);transition:background-position .4s,transform .2s,box-shadow .2s}
.card .format-btn:hover,.card button:not(.liked):hover{background-position:100% 0;box-shadow:0 6px 22px color-mix(in srgb,var(--c1) 55%,transparent)}
.card::before{content:"";position:absolute;inset:0;border-radius:inherit;background:radial-gradient(320px circle at var(--mx,50%) var(--my,50%),color-mix(in srgb,var(--c1) 20%,transparent),transparent 60%);opacity:0;transition:opacity .3s;pointer-events:none}
.card:hover::before{opacity:1}
.feat:nth-child(4n+1) i{filter:drop-shadow(0 0 12px var(--a))}.feat:nth-child(4n+2) i{filter:drop-shadow(0 0 12px #ff2bd6)}.feat:nth-child(4n+3) i{filter:drop-shadow(0 0 12px #ffd23f)}.feat:nth-child(4n) i{filter:drop-shadow(0 0 12px #39ff14)}
.feat:nth-child(4n+2):hover{border-color:#ff2bd6}.feat:nth-child(4n+3):hover{border-color:#ffd23f}.feat:nth-child(4n):hover{border-color:#39ff14}
#palBtn{position:fixed;right:14px;bottom:72px;z-index:60;width:46px;height:46px;border-radius:50%;padding:0;margin:0;font-size:20px;background:conic-gradient(from var(--ang),#ff3b30,#ffd23f,#39ff14,#00f0ff,#7b2ff7,#ff2bd6,#ff3b30)!important;animation:ang 5s linear infinite;box-shadow:0 0 18px rgba(255,255,255,.35)}
#palBtn::after{display:none}
#pal{position:fixed;right:14px;bottom:128px;z-index:65;width:min(310px,calc(100vw - 28px));padding:14px;border-radius:22px;background:rgba(8,8,22,.93);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--a);box-shadow:0 0 34px color-mix(in srgb,var(--a) 35%,transparent);display:none}
#pal.on{display:block;animation:rise .3s both}
#pal b{display:block;margin-bottom:8px;color:var(--a)}
#pal .g{display:grid;grid-template-columns:repeat(6,1fr);gap:7px;max-height:40vh;overflow:auto;margin-bottom:8px}

/* ===== v9 FAST + LUXURY ===== */
#matrix{display:none!important}
.card{animation:none!important}.card:hover{animation:ang 6s linear infinite!important}
.card,.feat,.hstats div,.faq details{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
#aur{left:50%!important;right:auto!important;top:50%!important;width:150vmax!important;height:150vmax!important;margin:-75vmax 0 0 -75vmax;border-radius:50%;filter:blur(60px);opacity:.28;background:conic-gradient(from 0deg,var(--a),var(--a2),transparent 28%,#ffd23f 48%,transparent 62%,var(--a));animation:spin2 80s linear infinite!important;will-change:transform}
.neon{filter:drop-shadow(0 0 8px currentColor)!important}
.win{animation:none!important}.car{display:none}
body.lite *,body.lite *::before,body.lite *::after{animation:none!important;transition:none!important}
body.lite #rain,body.lite #aur,body.lite .orb,body.lite #viz{display:none!important}
body.lite #tk{animation:tkm 45s linear infinite!important}
@media(prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;animation-iteration-count:1!important}}
.logo::after{content:"PRO";margin-inline-start:7px;font-size:.58rem;padding:2px 7px;border-radius:8px;color:#000;background:linear-gradient(90deg,#b8860b,#ffd700,#fff3b0);font-weight:900;vertical-align:middle;text-shadow:none}
.eyebrow{border-color:#ffd700!important;background:linear-gradient(90deg,rgba(255,215,0,.16),rgba(255,215,0,.04))!important;color:#ffe58a}
.sec h2::after{content:"◆";width:auto!important;height:auto!important;background:none!important;box-shadow:none!important;margin:6px auto 14px!important;color:#ffd700;-webkit-text-fill-color:#ffd700;font-size:.8rem;text-shadow:0 0 10px #ffd700}
.ft2{border-top-color:rgba(255,215,0,.5)!important}
input[type=range]{padding:0;height:8px;accent-color:var(--a)}
.swg{display:grid;grid-template-columns:repeat(auto-fill,minmax(44px,1fr));gap:6px;margin-top:8px}
.swg button{padding:8px 0;margin:0;font-size:1.1rem}
#imgC{width:100%;border-radius:14px;margin-top:10px;display:none;border:1px solid rgba(255,255,255,.2)}
#tour{position:fixed;left:50%;bottom:84px;transform:translateX(-50%);width:min(380px,calc(100vw - 24px));z-index:7000;background:rgba(8,8,22,.96);border:2px solid #ffd700;border-radius:20px;padding:16px;box-shadow:0 0 34px rgba(255,215,0,.35);display:none}
#tour.on{display:block}#tour p{line-height:1.8;margin-bottom:10px}#tour small{color:#ffd700}

/* ===== v10 ===== */
:root{--tk:34px}
#nav2{top:var(--tk)!important}
.container{padding-top:calc(var(--tk) + 68px)!important;padding-bottom:110px!important}
body{line-height:1.7}
.sec{margin:56px 0 12px!important}
.card{border-radius:22px!important;box-shadow:0 8px 30px rgba(0,0,0,.42),0 0 18px color-mix(in srgb,var(--c1) 10%,transparent)!important}
.card h3{font-size:1.05rem}
.format-btn,.card button{border-radius:30px}
#ticker{-webkit-mask-image:linear-gradient(90deg,transparent,#000 5%,#000 95%,transparent);mask-image:linear-gradient(90deg,transparent,#000 5%,#000 95%,transparent)}
#tk a{background:rgba(255,255,255,.07);border:1px solid color-mix(in srgb,var(--a) 45%,transparent);border-radius:20px;padding:2px 14px;margin:0 6px;font-size:.82rem;transition:.2s}
#tk a:hover{background:var(--a);color:#000}
#tk span{display:inline-block;color:var(--a);animation:spin2 4s linear infinite;margin:0 2px}
.appbox{max-width:620px;margin:0 auto;text-align:center;padding:28px 22px;border-radius:26px;background:linear-gradient(160deg,rgba(255,215,0,.12),rgba(10,12,28,.84) 45%),rgba(10,12,28,.84);border:1px solid rgba(255,215,0,.45);box-shadow:0 14px 46px rgba(0,0,0,.5)}
.appico{width:84px;height:84px;border-radius:22px;box-shadow:0 0 26px rgba(255,215,0,.4);margin-bottom:6px}
.appbox p{color:#c5c9e8;line-height:1.9;margin-bottom:16px;font-size:.95rem}
.appbtns{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.appbtns a{cursor:pointer}.appbox small{display:block;margin-top:12px;color:#9aa0c4}
.mbox{max-width:680px!important}
.acfg h4{margin:18px 0 2px;color:var(--a);font-size:.95rem}
.acfg label{display:block;margin-top:10px;font-size:.85rem;color:#ccd}
.acfg textarea{height:110px;direction:ltr}
.chk{display:inline-flex!important;align-items:center;gap:4px;margin:4px 10px 4px 0!important}
#nav{bottom:calc(12px + env(safe-area-inset-bottom))!important}
#palBtn{bottom:calc(72px + env(safe-area-inset-bottom))!important}
@media(max-width:380px){#nav button{width:40px;height:40px;font-size:17px}#nav{gap:2px}}

/* ===== v11 ROYAL : black / crimson / silver / gold (من هوية اللوجو) ===== */
:root{--bm:82%;--a:#ff2b2b;--a2:#a8001a;--b1:#050506;--b2:#14060a;--gold:#d9b25f;--gold2:#f3dd9b;--silver:#ececf1;--on:#fff;--panel:#0c0c11;--line:rgba(255,255,255,.09)}
html{background:#050506}
body{background:radial-gradient(120% 60% at 50% -8%,color-mix(in srgb,var(--a) 24%,transparent),transparent 62%),radial-gradient(100% 55% at 50% 112%,color-mix(in srgb,var(--a2) 34%,transparent),transparent 66%),linear-gradient(180deg,var(--b1),var(--b2) 55%,var(--b1))!important;background-size:auto!important;background-attachment:fixed!important;animation:none!important}
html::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.06;mix-blend-mode:overlay;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}
#rain,#scene,.car,.orb,#matrix{display:none!important}
#aur{opacity:.14!important}
::selection{background:var(--a);color:#fff}

/* نصوص وأزرار: لون النص يتحدد تلقائياً حسب لون الثيم */
button,.format-btn{color:var(--on)}
.btn-p{color:var(--on)}.num{color:var(--on)}.toast{color:var(--on)}
.card{--tc:var(--on)}
button::after{content:none!important;display:none!important}
button,.format-btn{border:1px solid rgba(255,255,255,.14);border-radius:12px;text-shadow:0 1px 0 rgba(0,0,0,.3);font-weight:800}
.format-btn,.card button{border-radius:12px}

/* العنوان: MODYX فضي + BIO أحمر زي اللوجو */
h1{display:block!important;width:fit-content;max-width:100%;margin:8px auto 0!important;font-size:clamp(2.1rem,9vw,3.3rem)!important;letter-spacing:.05em;
 background:linear-gradient(90deg,#fafafc 0,#bdbdc8 30%,#fafafc 58%,var(--a) 62%,var(--a2) 100%)!important;background-size:100% 100%!important;
 -webkit-background-clip:text!important;background-clip:text!important;-webkit-text-fill-color:transparent!important;animation:none!important;filter:drop-shadow(0 4px 16px rgba(0,0,0,.65))!important}
.hero-line{background:linear-gradient(90deg,transparent,var(--gold),transparent)!important;box-shadow:0 0 14px color-mix(in srgb,var(--gold) 60%,transparent)!important}
.tw{color:#d9d9e3}
.lead{color:#b9b9c6}

/* الهيرو: لوجو بحلقة دوارة */
.hero{padding-top:18px}
.hero-logo{position:relative;width:clamp(150px,44vw,212px);aspect-ratio:1;margin:4px auto 14px}
.hero-logo::before{content:"";position:absolute;inset:-9px;border-radius:50%;background:conic-gradient(from var(--ang),var(--a),transparent 28%,var(--gold),transparent 60%,var(--a));animation:ang 9s linear infinite}
.hero-logo img{position:relative;display:block;width:100%;height:100%;border-radius:50%;border:4px solid #050506;box-shadow:0 0 70px color-mix(in srgb,var(--a) 42%,transparent),0 24px 50px rgba(0,0,0,.6)}
.hero::before{background:radial-gradient(closest-side,color-mix(in srgb,var(--a) 22%,transparent),transparent 70%)!important}
.eyebrow{border-color:rgba(217,178,95,.55)!important;background:rgba(217,178,95,.08)!important;color:var(--gold2)!important}
.btn-p{background:linear-gradient(180deg,color-mix(in srgb,var(--a) var(--bm),#000),var(--a2));border:1px solid rgba(255,255,255,.18);box-shadow:0 12px 34px color-mix(in srgb,var(--a2) 55%,transparent),inset 0 1px 0 rgba(255,255,255,.28);border-radius:14px}
.btn-g{border:1px solid rgba(217,178,95,.6);color:var(--gold2);background:rgba(217,178,95,.06);border-radius:14px}
.btn-g:hover{background:rgba(217,178,95,.14)}
.hstats div{background:var(--panel);border:1px solid var(--line);border-radius:14px}
.hstats b{color:var(--gold2);text-shadow:none}
.by{color:#8f8fa0}

/* الكروت */
body .card,body .cols .card:nth-child(n){--c1:var(--a);--c2:var(--gold);--tc:var(--on);border:1px solid var(--line)!important;border-radius:20px!important;
 background:linear-gradient(180deg,rgba(255,255,255,.04),transparent 34%),var(--panel)!important;box-shadow:0 20px 54px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.05)!important}
.card:hover{animation:none!important}
.card::after{content:"";position:absolute;top:0;left:14%;right:14%;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:.55;pointer-events:none}
.card h3{color:var(--silver)!important;text-shadow:none!important;border-image:none!important;border-bottom:1px solid var(--line)!important}
.card .format-btn,.card button:not(.liked){background:linear-gradient(180deg,color-mix(in srgb,var(--a) var(--bm),#000),var(--a2));color:var(--on)}
.card .format-btn:hover,.card button:not(.liked):hover{box-shadow:0 8px 24px color-mix(in srgb,var(--a2) 60%,transparent)}
.tabs button.off{opacity:.4}
textarea,.preview,input,select{border:1px solid var(--line)}
textarea:focus,input:focus,select:focus{border-color:var(--a);box-shadow:0 0 0 3px color-mix(in srgb,var(--a) 22%,transparent)}
textarea,input,select{border-radius:12px!important;background:#08080c!important}
.item{background:#09090d;border:1px solid var(--line);border-radius:14px}
.stats div{background:#09090d;border:1px solid var(--line)}
.stats b{color:var(--gold2);text-shadow:none}

/* مميزات / خطوات / أسئلة */
.sec h2{background:linear-gradient(180deg,#fff,#c2c2ce)!important;-webkit-background-clip:text!important;background-clip:text!important;-webkit-text-fill-color:transparent!important}
.sec h2::after{color:var(--gold)!important;-webkit-text-fill-color:var(--gold)!important}
.feat{background:var(--panel);border:1px solid var(--line);border-radius:18px}
.sec .feat:nth-child(n):hover{border-color:color-mix(in srgb,var(--a) 70%,transparent);box-shadow:0 14px 36px color-mix(in srgb,var(--a2) 30%,transparent)}
.feat i{filter:drop-shadow(0 0 12px color-mix(in srgb,var(--a) 65%,transparent))!important}
.num{background:linear-gradient(135deg,var(--a),var(--a2));box-shadow:0 0 18px color-mix(in srgb,var(--a) 50%,transparent)}
.faq details{background:var(--panel);border:1px solid var(--line);border-radius:14px}
.faq details[open]{border-color:color-mix(in srgb,var(--a) 60%,transparent)}
.faq summary::after{color:var(--gold)}

/* الشريط العلوي */
#nav2{background:rgba(5,5,7,.82);border-bottom:1px solid rgba(217,178,95,.22)}
.logo{display:flex;align-items:center;gap:9px;color:var(--silver)!important;text-shadow:none!important}
.logo img{width:32px;height:32px;border-radius:50%;border:1px solid rgba(217,178,95,.6);box-shadow:0 0 12px color-mix(in srgb,var(--a) 50%,transparent)}
.logo::after{background:linear-gradient(90deg,#9a7418,var(--gold),var(--gold2))!important}
#ticker{background:rgba(5,5,7,.9);border-bottom:1px solid rgba(217,178,95,.25);box-shadow:none}
#ticker::after{background:linear-gradient(90deg,transparent,var(--a),var(--gold),var(--a),transparent)!important;height:2px!important;animation:none!important}
#tk a{border-color:rgba(217,178,95,.28)}
#nav{background:rgba(8,8,11,.9);border:1px solid rgba(217,178,95,.3)}
.ft2{border-top:1px solid rgba(217,178,95,.35)!important}
.fgrid b{color:var(--gold2)}
.copy{color:#8a8a99}

/* شاشات البوابة */
.captcha-box{background:rgba(12,12,17,.97)!important;border:1px solid rgba(217,178,95,.35)!important;box-shadow:0 0 80px color-mix(in srgb,var(--a) 22%,transparent)!important}
.captcha-box h2{color:var(--silver)!important;text-shadow:none!important}
.gate-logo{width:104px;height:104px;border-radius:50%;margin:0 auto 12px;display:block;border:2px solid rgba(217,178,95,.6);box-shadow:0 0 36px color-mix(in srgb,var(--a) 45%,transparent)}
.ttlogo{display:none}
a.big{background:#000;border:1px solid #fe2c55;color:#fff;border-radius:12px}
#loader{background:radial-gradient(circle at 50% 38%,#2b060c,#050506 70%)!important}
#loader::before{display:none!important}
.ld-logo{width:132px;height:132px;border-radius:50%;border:3px solid rgba(217,178,95,.7);animation:mpulse 1.6s infinite}
.lg{font-size:1.5rem!important;margin-top:18px;color:var(--silver)!important;text-shadow:none!important;letter-spacing:.08em}
.lbar{border-color:rgba(217,178,95,.5)!important}
#lfill{background:linear-gradient(90deg,var(--a2),var(--a),var(--gold))!important}

/* ===== شاشة الصلاة على النبي ﷺ ===== */
#sal{position:fixed;inset:0;z-index:9800;display:flex;align-items:center;justify-content:center;padding:22px;text-align:center;overflow:auto;
 background:radial-gradient(90% 60% at 50% 28%,#2e060d,#050506 72%)}
#sal.off{opacity:0;visibility:hidden;transition:opacity .9s,visibility .9s}
.sal-in{width:100%;max-width:440px;margin:auto}
.sal-logo{position:relative;width:150px;height:150px;margin:0 auto 18px}
.sal-logo::before{content:"";position:absolute;inset:-8px;border-radius:50%;background:conic-gradient(from var(--ang),var(--gold),transparent 35%,var(--a),transparent 70%,var(--gold));animation:ang 8s linear infinite}
.sal-logo img{position:relative;width:100%;height:100%;border-radius:50%;border:4px solid #050506;display:block}
.sal-ayah{font-family:'Amiri','Cairo',serif;font-size:clamp(1.3rem,5.6vw,1.75rem);line-height:2.1;color:var(--gold2);margin:6px 0 2px}
.sal-ref{font-size:.8rem;color:#8f8fa0;margin-bottom:26px}
.sal-btn{display:block;width:100%;padding:17px 14px;font-size:1.2rem!important;font-weight:900;font-family:inherit;border-radius:16px!important;cursor:pointer;
 background:linear-gradient(180deg,color-mix(in srgb,var(--a) var(--bm),#000),var(--a2))!important;color:#fff!important;border:1px solid rgba(255,255,255,.2)!important;
 box-shadow:0 14px 40px color-mix(in srgb,var(--a2) 60%,transparent),inset 0 1px 0 rgba(255,255,255,.3)!important;margin:0!important}
.sal-btn:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.sal-note{font-size:.78rem;color:#8f8fa0;margin-top:12px}
.sal-say{display:none}
#sal.go .sal-pre{display:none}
#sal.go .sal-say{display:block}
.sal-text{font-family:'Amiri','Cairo',serif;font-size:clamp(1.6rem,7vw,2.2rem);line-height:2.1;color:#fff;text-shadow:0 0 26px color-mix(in srgb,var(--a) 70%,transparent)}
.sal-bars{display:flex;gap:5px;justify-content:center;align-items:flex-end;height:42px;margin:18px 0 8px}
.sal-bars i{width:6px;border-radius:4px;background:linear-gradient(var(--gold2),var(--a));height:10px;animation:salbar 1s ease-in-out infinite}
.sal-bars i:nth-child(2n){animation-delay:.15s}.sal-bars i:nth-child(3n){animation-delay:.3s}.sal-bars i:nth-child(5n){animation-delay:.45s}
@keyframes salbar{0%,100%{height:8px}50%{height:40px}}
#sal.done .sal-bars{display:none}
.sal-thx{font-family:'Amiri','Cairo',serif;font-size:1.25rem;color:var(--gold2);min-height:2.2em;margin-top:6px}
.sal-cnt{margin-top:14px;font-size:.86rem;color:#a4a4b3}
.sal-cnt b{color:var(--gold2)}
.sal-foot{font-family:'Amiri','Cairo',serif;color:var(--gold2);font-size:1.15rem;margin-bottom:6px}

/* ===== قسم تحميل التطبيق ===== */
.appbox{position:relative;max-width:660px;padding:34px 22px 26px!important;border-radius:26px!important;border:1px solid rgba(217,178,95,.4)!important;overflow:hidden;
 background:radial-gradient(120% 70% at 50% 0,color-mix(in srgb,var(--a) 20%,transparent),transparent 62%),var(--panel)!important;box-shadow:0 26px 70px rgba(0,0,0,.6)!important}
.app-logo{position:relative;width:128px;height:128px;margin:0 auto 14px}
.app-logo::before{content:"";position:absolute;inset:-7px;border-radius:50%;background:conic-gradient(from var(--ang),var(--a),transparent 30%,var(--gold),transparent 66%,var(--a));animation:ang 8s linear infinite}
.app-logo .appico{position:relative;width:100%;height:100%;border-radius:50%;border:4px solid #0c0c11;margin:0;box-shadow:0 0 44px color-mix(in srgb,var(--a) 40%,transparent)}
.appbox h2{font-size:1.5rem!important}
.app-chips{list-style:none;display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:0 0 20px;padding:0}
.app-chips li{padding:6px 14px;border-radius:30px;font-size:.84rem;font-weight:700;color:var(--gold2);border:1px solid rgba(217,178,95,.4);background:rgba(217,178,95,.07)}
.appbtns{margin-bottom:6px}
.app-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:22px;text-align:right}
.app-steps div{background:#09090d;border:1px solid var(--line);border-radius:16px;padding:14px 16px}
.app-steps b{display:block;color:var(--gold2);margin-bottom:6px;font-size:.95rem}
.app-steps ol{margin:0;padding:0 18px 0 0;color:#b9b9c6;font-size:.85rem;line-height:1.9}
.appbox small{color:var(--gold2)!important}

/* لوحة قديمة (المودال) */
.mbox{background:rgba(12,12,17,.98);border:1px solid rgba(217,178,95,.4)}
.mbox h3{color:var(--gold2)}
@media(prefers-reduced-motion:reduce){.hero-logo::before,.app-logo::before,.sal-logo::before,.sal-bars i,.ld-logo{animation:none!important}}

.pbuh{font-family:'Amiri','Noto Naskh Arabic','Scheherazade New',serif}
@media(max-width:600px){#secFeat .grid3{grid-template-columns:1fr 1fr;gap:10px}#secFeat .feat{padding:14px 10px}#secFeat .feat p{font-size:.78rem;line-height:1.6}#secFeat .feat i{font-size:1.6rem}#secFeat .feat b{font-size:.95rem}}
</style>
</head>
<body>

<!-- ===== بوابة الصلاة على النبي ﷺ ===== -->
<div id="sal" role="dialog" aria-modal="true" aria-label="الصلاة على النبي">
 <div class="sal-in">
  <div class="sal-logo"><img src="/logo.png" alt="MODYXBIO" width="150" height="150"></div>
  <div class="sal-pre">
   <p class="sal-ayah">﴿ إِنَّ اللَّهَ وَمَلَائِكَتَهُ يُصَلُّونَ عَلَى النَّبِيِّ ۚ يَا أَيُّهَا الَّذِينَ آمَنُوا صَلُّوا عَلَيْهِ وَسَلِّمُوا تَسْلِيمًا ﴾</p>
   <div class="sal-ref">سورة الأحزاب • الآية ٥٦</div>
   <button class="sal-btn" id="salBtn" type="button">صلِّ على النبي <span class="pbuh">ﷺ</span> وادخل</button>
   <div class="sal-note">اضغط الزر وسيُسمعك الموقع الصلاة على النبي <span class="pbuh">ﷺ</span> بصوت، رددها معنا ثم ادخل.</div>
  </div>
  <div class="sal-say">
   <div class="sal-text">اللهم صلِّ وسلِّم وبارك على سيدنا محمد <span class="pbuh">ﷺ</span></div>
   <div class="sal-bars"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
   <div class="sal-thx" id="salThx"></div>
  </div>
  <div class="sal-cnt" id="salCnt"></div>
 </div>
</div>
<script>try{if(sessionStorage.getItem('mx_sal')==='1'){var _s=document.getElementById('sal');if(_s)_s.remove()}}catch(e){}</script>

<!-- ===== CAPTCHA OVERLAY - ALWAYS SHOWN ON PAGE LOAD ===== -->
<div id="captchaOverlay">
    <div class="captcha-box">
        <img class="gate-logo" src="/logo.png" alt="" width="104" height="104">
        <h2>🔒 التحقق البشري</h2>
        <p class="sub-text">أكد إنك إنسان عشان تدخل الأداة</p>
        <div class="captcha-lock"><i class="fas fa-shield-alt"></i> محمي بنظام أمان متقدم</div>
        
        <div class="captcha-slider-container" id="sliderContainer">
            <div class="captcha-slider-track">
                <div class="captcha-slider-fill" id="sliderFill"></div>
                <span class="captcha-progress-text" id="progressText">اسحب للتحقق</span>
            </div>
            <div class="captcha-slider-thumb" id="sliderThumb">
                <i class="fas fa-chevron-right"></i>
            </div>
        </div>
        <div class="captcha-status" id="captchaStatus">👉 اسحب الزر لليمين</div>
        <button class="captcha-refresh" onclick="resetCaptcha()">⟳ تحديث</button>
        <div class="captcha-footer">
            <i class="fas fa-check-circle"></i> اتصال آمن
            <i class="fas fa-circle" style="font-size:4px; color:#333;"></i>
            <i class="fas fa-clock"></i> الجلسة نشطة
        </div>
    </div>
</div>

<!-- ===== RESULT OVERLAY ===== -->
<div id="overlay">
    <i id="res-icon" class="fas fa-check-circle res-icon"></i>
    <div id="res-title" class="res-title"></div>
    <div id="res-body" class="res-body"></div>
</div>

<canvas id="matrix"></canvas>
<div class="container">
    <section class="hero">
        <div class="hero-logo"><img src="/logo.png" alt="MODYXBIO" width="212" height="212" fetchpriority="high"></div>
        <div class="eyebrow" id="cEye">🇪🇬 الشرق الأوسط • ME</div>
        <h1>𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</h1>
        <div class="tw" id="tw"></div>
        <p class="lead" id="cLead">محرر بايو احترافي بألوان وتنسيقات لا نهائية، وقوالب جاهزة، ومعرض عام تشوف فيه بايوهات الناس وتستخدمها.</p>
        <div class="cta"><a class="btn-p" href="#secEd">✏️ ابدأ دلوقتي</a><a class="btn-g" href="#secGal">🌍 شوف المعرض</a><a class="btn-g" href="https://t.me/MODYXBOT1" target="_blank" rel="noopener">🤖 تواصل تليجرام</a></div>
        <div class="hstats"><div><b id="hV">0</b><small>زائر</small></div><div><b id="hU">0</b><small>تحديث ناجح</small></div><div><b id="hR">—</b><small>التقييم</small></div></div>
        <div class="by">𝑫𝒆𝒗: 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅 • 𝑭𝑴𝑺: 𝒁𝑨𝑨𝑻𝑨𝑹</div>
    </section>

    <div class="card" id="secEd">
        <h3>✏️ محرر البايو</h3>
        <textarea id="bio" placeholder="اكتب البايو بتاعك هنا..."></textarea>
        <div id="charCount" style="text-align:right; font-size:12px; margin-top:5px;">0 / 250</div>
        <div class="preview" id="preview">معاينة مباشرة</div>
        <div style="margin-top:8px"><button class="format-btn" onclick="copyBio($('bio').value)">📋 نسخ</button><button class="format-btn" onclick="shareBio()">🔗 مشاركة</button><button class="format-btn" onclick="saveBio()">💾 حفظ</button></div>
    </div>

    <div class="card" id="secTpl">
        <h3>⚡ قوالب بايو جاهزة (اضغط واستخدم)</h3>
        <div class="chips" id="tpls"></div>
    </div>

    <div class="card" id="secFmt">
        <h3>🎨 التنسيق</h3>
        <button class="format-btn" onclick="insertSimple('[b]')">عريض</button>
        <button class="format-btn" onclick="insertSimple('[i]')">مائل</button>
        <button class="format-btn" onclick="insertSimple('[c]')">منحني</button>
        <button class="format-btn" onclick="insertSimple('[u]')">تحته خط</button>
        <button class="format-btn" onclick="insertSimple('[s]')">مشطوب</button>
    </div>

    <div class="card" id="secBC">
        <h3>🌈 ألوان البايو (كل ألوان العالم)</h3>
        <div class="colors-ribbon" id="colorRibbon"></div>
    </div>



    <div class="card" id="secCol">
        <h3>🖌️ ألوان الموقع والخلفية</h3>
        <div class="themes" id="themes"></div>
        <div class="row"><label>🎨 لون الخلفية الأول</label><input type="color" id="c1" value="#050510"></div>
        <div class="row"><label>🎨 لون الخلفية الثاني</label><input type="color" id="c2" value="#0b1a2e"></div>
        <div class="row"><label>✨ لون الموقع الأساسي</label><input type="color" id="c3" value="#00ffc3"></div>
        <div class="row"><label>💫 لون الموقع الثانوي</label><input type="color" id="c5" value="#0099ff"></div>
        <div class="row"><label>📱 لون شريط المتصفح</label><input type="color" id="c4" value="#00ffc3"></div>
        <button class="format-btn" onclick="randomTheme()">🎲 عشوائي</button>
        <button class="format-btn" id="rbBtn" onclick="toggleRainbow()">🌈 قوس قزح</button>
        <button class="format-btn" onclick="applyT(...TH[0])">↺ الافتراضي</button>
    </div>
    <div class="card" id="secAuth">
        <h3>🔐 طريقة الدخول</h3>
        <select id="method" onchange="togglePassword()">
            <option value="jwt">JWT Token (مباشر)</option>
            <option value="uid">UID & الباسورد</option>
            <option value="access">Access Token</option>
            <option value="eat">EAT Token</option>
        </select>
        <select id="serverSelect" style="margin-top: 10px;">
            <option value="ME" selected>🇪🇬 ME - الشرق الأوسط (مصر)</option>
            <option value="IND">🇮🇳 IND - الهند</option>
            <option value="BD">🇧🇩 BD - بنجلاديش</option>
            <option value="SG">🇸🇬 SG - سنغافورة</option>
            <option value="BR">🇧🇷 BR - البرازيل</option>
            <option value="US">🇺🇸 US - أمريكا</option>
            <option value="EU">🇪🇺 EU - أوروبا</option>
        </select>
        <input id="token" placeholder="التوكن / UID" autocomplete="off">
        <input id="password" placeholder="الباسورد" type="password" style="display:none;">
        <label class="pub"><input type="checkbox" id="pubChk" checked> نشر البايو في المعرض العام (بيظهر نص البايو بس، من غير توكن أو UID)</label>
        <button id="submitBtn" onclick="handleSubmit()" style="width:100%; margin-top:15px;" disabled>🔒 تحقق الأول</button>
    </div>

    <div class="card" id="secGal"><h3>🌍 معرض البايوهات العام</h3>
        <div class="tabs"><button class="format-btn" id="tNew" onclick="galSort('new')">🕒 الأحدث</button><button class="format-btn off" id="tTop" onclick="galSort('top')">🔥 الأكثر إعجاباً</button></div>
        <div id="galList"></div>
    </div>
    <div class="card" id="secStats"><h3>📊 إحصائيات الموقع</h3><div class="stats"><div><b id="stV">0</b><small>👁️ زوار الموقع</small></div><div><b id="stU">0</b><small>✅ تحديثات ناجحة</small></div><div><b id="stM">0</b><small>🙋 تحديثاتك أنت</small></div></div></div>
    <div class="card" id="secRate" style="text-align:center"><h3>⭐ قيّم الموقع</h3><div id="stars"></div><div style="font-size:.9rem;margin-top:4px">المتوسط: <b id="avg">—</b></div></div>
    <div class="card" id="secSaved"><h3>💾 بايوهاتي المحفوظة</h3><div id="savedList"></div></div>
    <div class="card" id="secHist"><h3>🕘 سجل التحديثات</h3><div id="histList"></div><button class="format-btn" onclick="clearHist()" style="margin-top:10px">🗑️ مسح السجل</button></div>

    <div class="card" id="secGb"><h3>📖 دفتر الزوار</h3>
        <input id="gbName" placeholder="اسمك" maxlength="30">
        <textarea id="gbText" placeholder="اكتب تعليقك هنا..." maxlength="200" style="height:80px"></textarea>
        <button class="format-btn" onclick="gbSend()" style="margin-top:8px">📨 إرسال التعليق</button>
        <div id="gbList"></div>
    </div>

    <div class="card" id="secShare" style="text-align:center"><h3>📣 شارك الموقع</h3>
        <div id="shr" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center"></div>
    </div>

    <div class="card" id="secMsg"><h3>✉️ ابعت رسالة للمطور</h3>
        <input id="mName" placeholder="اسمك (اختياري)">
        <textarea id="mText" placeholder="اكتب رسالتك..." style="height:90px"></textarea>
        <div style="margin-top:8px"><button class="sb" style="background:#25D366" onclick="msgTo('wa')"><i class="fab fa-whatsapp"></i> واتساب</button> <button class="sb" style="background:#229ED9" onclick="msgTo('tg')"><i class="fab fa-telegram"></i> تليجرام</button> <button class="sb" style="background:#000;border:2px solid #fe2c55" onclick="msgTo('tt')"><i class="fab fa-tiktok"></i> تيك توك</button></div>
        <div style="font-size:.75rem;color:#aaa;margin-top:6px">في تليجرام وتيك توك الرسالة بتتنسخ تلقائي، والصقها في المحادثة.</div>
    </div>

    <section class="sec" id="secFeat"><h2>ليه 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶؟</h2><div class="grid3">
        <div class="feat"><i>⚡</i><b>سريع</b><p>حدّث البايو في ثواني من أي جهاز.</p></div>
        <div class="feat"><i>🔐</i><b>خصوصيتك</b><p>ما بنخزنش التوكن ولا الباسورد عندنا.</p></div>
        <div class="feat"><i>♾️</i><b>مجاني</b><p>كل المميزات بدون اشتراك ولا مقابل.</p></div>
        <div class="feat"><i>⭐</i><b>متاح 24/7</b><p>الموقع شغال طول اليوم من أي مكان.</p></div>
        <div class="feat"><i>🎨</i><b>ألوان لا نهائية</b><p>أكتر من 100 لون وتنسيقات وقوالب جاهزة.</p></div>
        <div class="feat"><i>🌍</i><b>معرض عام</b><p>شوف بايوهات الناس واستخدمها واعمل لايك.</p></div></div></section>
    <section class="sec" id="secHow"><h2>إزاي تستخدمه؟</h2><div class="grid3">
        <div class="feat"><span class="num">1</span><b>اختار طريقة الدخول</b><p>اختار نوع التوكن والسيرفر، وحط بياناتك.</p></div>
        <div class="feat"><span class="num">2</span><b>اكتب وزخرف</b><p>اكتب البايو وزوّقه بالألوان أو استخدم قالب جاهز.</p></div>
        <div class="feat"><span class="num">3</span><b>دوس تحديث</b><p>اتحقق إنك إنسان وادوس تحديث البايو.</p></div></div></section>
    <section class="sec faq" id="secFaq"><h2>أسئلة شائعة</h2>
        <details><summary>إيه هو التوكن؟</summary><p>مفتاح دخول مؤقت للحساب، بيستخدمه الموقع عشان يحدّث البايو. ما بنحفظهوش عندنا.</p></details>
        <details><summary>ليه التحقق البشري؟</summary><p>عشان نحمي الموقع من الروبوتات والضغط الزايد.</p></details>
        <details><summary>البايو بتاعي بيظهر لمين؟</summary><p>لو سبت علامة النشر مفعّلة، نص البايو بس بيظهر في المعرض العام، من غير أي بيانات حساب.</p></details>
        <details><summary>لو حصلت مشكلة أكلم مين؟</summary><p>كلّم المطور على تليجرام @MODYXBOT1 أو واتساب 01204564384.</p></details></section>
    <div class="card" id="secCt" style="text-align:center">
        <h3>📞 تواصل مع المطور</h3>
        <div class="social">
            <a class="tg" href="https://t.me/MODYXBOT1" target="_blank" rel="noopener"><i class="fab fa-telegram"></i></a>
            <a class="tt" href="https://www.tiktok.com/@king_burd" target="_blank" rel="noopener"><i class="fab fa-tiktok"></i></a>
            <a class="wa" href="https://wa.me/201204564384" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i></a>
        </div>
        <div class="devbox"><div><span>𝑫𝒆𝒗:</span> 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅</div><div><span>𝑭𝑴𝑺:</span> 𝒁𝑨𝑨𝑻𝑨𝑹</div></div>
        <div style="font-size:.85rem;color:#ccc">@MODYXBOT1 • @king_burd • 01204564384</div>
        <div class="stamp"><small>DEVELOPER</small><i class="fas fa-star"></i><b>𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</b><small>★ EGYPT ★</small></div>
    </div>
    <section class="sec" id="secApp"><div class="appbox">
        <div class="app-logo"><img class="appico" src="/logo.png" alt="MODYXBIO" width="128" height="128" loading="lazy"></div>
        <h2 id="appH">حمّل تطبيق 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</h2>
        <p id="appP">ثبّته على موبايلك وافتحه بضغطة زي أي تطبيق، سريع وبملء الشاشة.</p>
        <ul class="app-chips"><li>⚡ سريع</li><li>🛡️ آمن</li><li>♾️ مجاني</li><li>⭐ متاح 24/7</li></ul>
        <div class="appbtns"><a class="btn-p" id="appInst" href="#">📲 تثبيت التطبيق</a><a class="btn-g" id="appApk" href="#" target="_blank" rel="noopener" style="display:none">⬇️ تحميل APK</a><a class="btn-g" href="https://t.me/MODYXBOT1" target="_blank" rel="noopener">🤖 تواصل تليجرام</a></div>
        <div class="app-steps">
         <div><b>أندرويد</b><ol><li>افتح الموقع في كروم</li><li>اضغط ⋮ ثم «تثبيت التطبيق»</li><li>افتحه من الشاشة الرئيسية</li></ol></div>
         <div><b>آيفون</b><ol><li>افتح الموقع في سفاري</li><li>اضغط زر المشاركة ⬆️</li><li>اختر «إضافة إلى الشاشة الرئيسية»</li></ol></div>
        </div>
        <small id="appHint"></small></div></section>
    <footer class="ft2"><div class="fgrid">
        <div><b>🐉 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</b><p style="color:#9aa0c4;font-size:.85rem;line-height:1.8">محرر بايو للشرق الأوسط 🇪🇬</p></div>
        <div><b>روابط</b><a href="#secEd">المحرر</a><a href="#secGal">المعرض</a><a href="#secHow">كيف يعمل</a><a href="#secFaq">الأسئلة</a><a href="#" id="instBtn" style="display:none">📲 ثبّت التطبيق</a><a href="#" onclick="startTour();return false">🧭 جولة</a></div>
        <div><b>تواصل</b><a href="https://t.me/MODYXBOT1" target="_blank" rel="noopener">تليجرام</a><a href="https://www.tiktok.com/@king_burd" target="_blank" rel="noopener">تيك توك</a><a href="https://wa.me/201204564384" target="_blank" rel="noopener">واتساب</a></div></div>
        <div class="copy"><div class="sal-foot">اللهم صلِّ وسلِّم على سيدنا محمد ﷺ</div>© 2026 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 🇪🇬 • 𝑫𝒆𝒗: 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅 • 𝑭𝑴𝑺: 𝒁𝑨𝑨𝑻𝑨𝑹<br><a href="/admin" style="color:#777;text-decoration:none">🔐 لوحة المطور</a></div></footer>
</div>

<button id="langBtn" onclick="toggleLang()">🌐 EN</button>
<div class="modal" id="help"><div class="mbox"><h3>📲 تثبيت التطبيق</h3><p id="helpT" style="line-height:1.9"></p><button class="format-btn" onclick="$('help').classList.remove('on')" style="width:100%;margin-top:10px">تمام</button></div></div>
<div class="modal" id="adm"><div class="mbox">
 <div id="admLogin"><h3>🔐 لوحة المطور</h3><input id="admPass" type="password" placeholder="كلمة السر"><button class="format-btn" style="width:100%;margin-top:10px" onclick="admLogin()">دخول</button></div>
 <div id="admPanel" style="display:none">
  <h3>📊 ملخص</h3><div id="admStats" class="item"></div>
  <div id="admCfg" class="acfg"></div>
  <h3 style="margin-top:12px">📢 إعلانات الشريط (سطر لكل إعلان: النص | الرابط)</h3>
  <textarea id="admAds" style="height:140px;direction:ltr"></textarea>
  <button class="format-btn" onclick="admSaveAds()">💾 حفظ الإعلانات</button>
  <h3 style="margin-top:12px">💬 تعليقات الزوار</h3><div id="admGb"></div>
  <h3 style="margin-top:12px">🌍 المعرض العام</h3><div id="admGal"></div>
  <button class="format-btn" onclick="admReset()" style="margin-top:10px">♻️ تصفير الإحصائيات</button>
 </div>
 <button class="format-btn" onclick="admClose()" style="width:100%;margin-top:12px;background:#444;color:#fff">إغلاق</button>
</div></div>
<header id="nav2"><a class="logo" href="#"><img src="/logo.png" alt="" width="32" height="32">𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</a><nav class="lk"><a href="#secEd">المحرر</a><a href="#secGal">المعرض</a><a href="#secCol">الألوان</a><a href="#secHow">كيف يعمل</a><a href="#secFaq">الأسئلة</a><a href="#secCt">تواصل</a></nav></header>
<div id="ticker"><div id="tk"></div></div>
<div id="loader"><img class="ld-logo" src="/logo.png" alt="" width="132" height="132"><div class="lg">𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</div><div class="lbar"><div id="lfill"></div></div><div id="lpct">0%</div><div id="ltxt">جاري التحميل...</div></div>
<div id="welcome" class="gate-w" style="position:fixed;inset:0;background:rgba(0,0,0,.94);backdrop-filter:blur(26px);display:flex;justify-content:center;align-items:center;padding:20px">
 <div class="captcha-box" style="animation:none">
  <img class="gate-logo" src="/logo.png" alt="" width="104" height="104">
  <h2>أهلاً بك في 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</h2>
  <div style="font-size:.8rem;color:#ddd;margin-bottom:8px">𝑫𝒆𝒗: 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅 • 𝑭𝑴𝑺: 𝒁𝑨𝑨𝑻𝑨𝑹</div>
  <p class="sub-text">تابعني على تيك توك الأول عشان توصلك كل الجديد 🔥<br>وبعدها اضغط دخول</p>
  <a class="big" href="https://www.tiktok.com/@king_burd" target="_blank" rel="noopener"><i class="fab fa-tiktok"></i> صفحتي على تيك توك</a>
  <button class="big" id="enterBtn">🚀 دخول الموقع</button>
 </div>
</div>
<audio id="bgm" src="/music" loop preload="none"></audio>
<canvas id="viz" width="240" height="92"></canvas>
<button id="musicBtn" onclick="toggleMusic()" title="الموسيقى"><i class="fas fa-volume-high" id="mi"></i></button>
<a id="ttFloat" href="https://www.tiktok.com/@king_burd" target="_blank" rel="noopener" title="تيك توك"><i class="fab fa-tiktok"></i></a>

<script>
// ========== MATRIX BACKGROUND ==========
const canvas = document.getElementById("matrix");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const letters = "MODYXBIO01";
const fontSize = 14;
const columns = canvas.width / fontSize;
const drops = [];
for (let i = 0; i < columns; i++) drops[i] = 1;
function drawMatrix() {
    ctx.fillStyle = "rgba(0,0,0,0.05)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--a").trim() || "var(--a)";
    ctx.font = fontSize + "px monospace";
    for (let i = 0; i < drops.length; i++) {
        let text = letters[Math.floor(Math.random() * letters.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    }
    requestAnimationFrame(drawMatrix);
}
drawMatrix();

// ========== UTILITY FUNCTIONS ==========
function showResult(type, title, html) {
    const ov = document.getElementById('overlay');
    ov.className = type + " active";
    document.getElementById('res-icon').className = type === 'success' ? "fas fa-check-circle res-icon" : "fas fa-times-circle res-icon";
    document.getElementById('res-title').innerText = title;
    document.getElementById('res-body').innerHTML = html;
    setTimeout(() => { ov.className = ""; }, 5000);
}

function insertSimple(tag) {
    let bio = document.getElementById("bio");
    let start = bio.selectionStart;
    let end = bio.selectionEnd;
    let text = bio.value;
    let newText = text.substring(0, start) + tag + text.substring(end);
    bio.value = newText;
    bio.focus();
    bio.setSelectionRange(start + tag.length, start + tag.length);
    updatePreview();
}

function insertColor(color) {
    insertSimple('[' + color + ']');
}

function togglePassword() {
    let m = document.getElementById("method").value;
    let pwdField = document.getElementById("password");
    pwdField.style.display = (m === "uid") ? "block" : "none";
}

let lastValidBio = "";
function updatePreview() {
    let bio = document.getElementById("bio");
    if (bio.value.length > 250) {
        bio.value = lastValidBio;
        return;
    }
    lastValidBio = bio.value;
    document.getElementById("charCount").innerText = bio.value.length + " / 250";
    let raw = bio.value;
    let text = raw.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
    let result = '';
    let i = 0;
    let currentColor = null;
    let currentBold = false, currentItalic = false, currentCurve = false, currentUnderline = false, currentStrike = false;
    
    function applyCurrent() {
        let style = '';
        if (currentColor) style += `color:#${currentColor};`;
        if (currentBold) style += `font-weight:bold;`;
        if (currentItalic) style += `font-style:italic;`;
        if (currentCurve) style += `font-style:italic;`;
        if (currentUnderline) style += `text-decoration:underline;`;
        if (currentStrike) style += `text-decoration:line-through;`;
        if (style) return `<span style="${style}">`;
        return '';
    }
    
    let buffer = '';
    while (i < text.length) {
        if (text[i] === '[') {
            if (buffer) {
                let open = applyCurrent();
                result += open + buffer + (open ? '</span>' : '');
                buffer = '';
            }
            let endIdx = text.indexOf(']', i);
            if (endIdx === -1) {
                buffer += text[i];
                i++;
                continue;
            }
            let tag = text.substring(i+1, endIdx);
            i = endIdx + 1;
            if (/^[0-9A-Fa-f]{6}$/.test(tag)) {
                currentColor = tag;
            } else if (tag === 'b') {
                currentBold = !currentBold;
            } else if (tag === 'i') {
                currentItalic = !currentItalic;
            } else if (tag === 'c') {
                currentCurve = !currentCurve;
            } else if (tag === 'u') {
                currentUnderline = !currentUnderline;
            } else if (tag === 's') {
                currentStrike = !currentStrike;
            } else {
                buffer += '[' + tag + ']';
            }
        } else {
            buffer += text[i];
            i++;
        }
    }
    if (buffer) {
        let open = applyCurrent();
        result += open + buffer + (open ? '</span>' : '');
    }
    document.getElementById("preview").innerHTML = result || "معاينة مباشرة";
}

// ========== COLOR RIBBON ==========
const colors = ["#FF0000","#DC143C","#B22222","#8B0000","#FA8072","#FF7F50","#FF8C00","#FFA500","#FFD700","#FFFF00","#F0E68C","#98FB98","#00FF00","#32CD32","#00FF7F","#008000","#2E8B57","#556B2F","#808000","#40E0D0","#00FFFF","#00BFFF","#1E90FF","#4682B4","#0000FF","#0000CD","#00008B","#191970","#8A2BE2","#9370DB","#800080","#4B0082","#FF00FF","#EE82EE","#DA70D6","#FF1493","#FF69B4","#FFC0CB","#D2B48C","#D2691E","#A0522D","#8B4513","#FFFFFF","#C0C0C0","#A9A9A9","#808080","#696969","#2F4F4F","#000000"];
const ribbon = document.getElementById("colorRibbon");
colors.forEach(col => {
    let dot = document.createElement("div");
    dot.className = "c-dot";
    dot.style.backgroundColor = col;
    dot.onclick = () => insertColor(col.substring(1));
    ribbon.appendChild(dot);
});

document.getElementById("bio").addEventListener("input", updatePreview);
updatePreview();

// ========== FIXED: SMART CAPTCHA (Touch Optimized) ==========
let captchaVerified = false;
let isDragging = false;
let startX = 0;
let currentX = 0;
let thumbLeft = 2;

const sliderContainer = document.getElementById('sliderContainer');
const sliderThumb = document.getElementById('sliderThumb');
const sliderFill = document.getElementById('sliderFill');
const progressText = document.getElementById('progressText');
const captchaStatus = document.getElementById('captchaStatus');
const captchaOverlay = document.getElementById('captchaOverlay');
const submitBtn = document.getElementById('submitBtn');

function getMaxLeft() {
    return sliderContainer.offsetWidth - sliderThumb.offsetWidth - 4;
}

function updateSlider(x) {
    const maxLeft = getMaxLeft();
    let left = Math.max(0, Math.min(x, maxLeft));
    const percent = (left / maxLeft) * 100;
    
    sliderThumb.style.left = (left + 2) + 'px';
    sliderFill.style.width = percent + '%';
    progressText.textContent = Math.round(percent) + '%';
    
    return left;
}

function handleStart(clientX) {
    const rect = sliderContainer.getBoundingClientRect();
    isDragging = true;
    startX = clientX - rect.left - sliderThumb.offsetWidth / 2;
    const currentLeft = parseFloat(sliderThumb.style.left) || 2;
    thumbLeft = currentLeft - 2;
    
    sliderThumb.style.transition = 'none';
    sliderFill.style.transition = 'none';
    sliderContainer.classList.add('active');
    
    captchaStatus.textContent = '🔓 كمّل سحب...';
    captchaStatus.className = 'captcha-status';
    
    updateSlider(thumbLeft + (clientX - rect.left - sliderThumb.offsetWidth / 2 - startX));
}

function handleMove(clientX) {
    if (!isDragging) return;
    
    const rect = sliderContainer.getBoundingClientRect();
    const maxLeft = getMaxLeft();
    let newLeft = thumbLeft + (clientX - rect.left - sliderThumb.offsetWidth / 2 - startX);
    newLeft = Math.max(0, Math.min(newLeft, maxLeft));
    
    updateSlider(newLeft);
    
    if (newLeft >= maxLeft - 2) {
        isDragging = false;
        captchaVerified = true;
        captchaStatus.textContent = '✅ تم التحقق بنجاح!';
        captchaStatus.className = 'captcha-status verified';
        progressText.textContent = '✅ تم';
        sliderThumb.style.background = 'linear-gradient(135deg, var(--a), #00cc88)';
        sliderThumb.innerHTML = '<i class="fas fa-check"></i>';
        sliderContainer.classList.remove('active');
        
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 تحديث البايو';
        submitBtn.style.opacity = '1';
        
        setTimeout(() => {
            captchaOverlay.classList.add('hidden');
        }, 500);
    }
}

function handleEnd() {
    if (isDragging) {
        isDragging = false;
        sliderContainer.classList.remove('active');
        
        const maxLeft = getMaxLeft();
        const currentLeft = parseFloat(sliderThumb.style.left) || 2;
        
        if (currentLeft - 2 < maxLeft - 20) {
            sliderThumb.style.transition = 'left 0.4s ease';
            sliderFill.style.transition = 'width 0.4s ease';
            sliderThumb.style.left = '2px';
            sliderFill.style.width = '0%';
            progressText.textContent = 'اسحب للتحقق';
            captchaStatus.textContent = '👉 اسحب لآخر الشريط';
            captchaStatus.className = 'captcha-status';
            thumbLeft = 0;
        }
    }
}

sliderContainer.addEventListener('mousedown', function(e) {
    e.preventDefault();
    handleStart(e.clientX);
});

document.addEventListener('mousemove', function(e) {
    if (isDragging) {
        e.preventDefault();
        handleMove(e.clientX);
    }
});

document.addEventListener('mouseup', function(e) {
    if (isDragging) {
        handleEnd();
    }
});

sliderContainer.addEventListener('touchstart', function(e) {
    e.preventDefault();
    const touch = e.touches[0];
    handleStart(touch.clientX);
}, { passive: false });

document.addEventListener('touchmove', function(e) {
    if (isDragging) {
        e.preventDefault();
        const touch = e.touches[0];
        handleMove(touch.clientX);
    }
}, { passive: false });

document.addEventListener('touchend', function(e) {
    if (isDragging) {
        handleEnd();
    }
}, { passive: false });

function resetCaptcha() {
    captchaVerified = false;
    isDragging = false;
    thumbLeft = 0;
    
    sliderThumb.style.transition = 'left 0.4s ease';
    sliderFill.style.transition = 'width 0.4s ease';
    sliderThumb.style.left = '2px';
    sliderFill.style.width = '0%';
    progressText.textContent = 'اسحب للتحقق';
    captchaStatus.textContent = '🔄 تم إعادة التحقق';
    captchaStatus.className = 'captcha-status';
    sliderThumb.style.background = 'linear-gradient(135deg, var(--a), var(--a2))';
    sliderThumb.innerHTML = '<i class="fas fa-chevron-right"></i>';
    sliderContainer.classList.remove('active');
    
    captchaOverlay.classList.remove('hidden');
    submitBtn.disabled = true;
    submitBtn.textContent = '🔒 تحقق الأول';
}

// ========== MAIN SUBMIT HANDLER ==========
async function handleSubmit() {
    if (!captchaVerified) {
        captchaOverlay.classList.remove('hidden');
        resetCaptcha();
        return;
    }
    
    await updateBio();
}

async function updateBio() {
    let method = document.getElementById("method").value;
    let token = document.getElementById("token").value.trim();
    let bio = document.getElementById("bio").value;
    let password = document.getElementById("password").value.trim();
    let server = document.getElementById("serverSelect").value;
    let btn = document.getElementById("submitBtn");
    
    if (!token) { alert("التوكن مطلوب!"); return; }
    if (!bio) { alert("اكتب البايو الأول!"); return; }
    if (bio.length < 3) { alert("البايو قصير - 3 حروف على الأقل"); return; }
    
    let body = { token, bio, server, method, publish: document.getElementById("pubChk").checked };
    if (method === "uid") {
        if (!password) { alert("الباسورد مطلوب!"); return; }
        body.password = password;
    }
    
    let original = btn.innerText;
    btn.innerText = "⏳ جاري التنفيذ...";
    btn.disabled = true;
    
    try {
        let res = await fetch("/api/update", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify(body)
        });
        let data = await res.json();
        
        if (data.status === "success") {
            showResult('success', '✅ تم بنجاح!', `
                <div style="text-align:center; padding:10px;">
                    <div style="margin:5px 0;"><strong>🆔 UID:</strong> ${data.uid || data.user_id || 'N/A'}</div>
                    <div style="margin:5px 0;"><strong>👤 الاسم:</strong> ${data.name || 'N/A'}</div>
                    <div style="margin:5px 0;"><strong>🌍 المنطقة:</strong> ${data.region_used || 'N/A'}</div>
                    <div style="margin:5px 0;"><strong>🔑 الطريقة:</strong> ${data.login_method || 'N/A'}</div>
                    <div style="margin-top:10px; color:var(--a);">✅ ${data.message || 'تم تحديث البايو بنجاح'}</div>
                </div>
            `);
            
            document.getElementById("token").value = "";
            document.getElementById("password").value = "";
            document.getElementById("bio").value = "";
            lastValidBio = "";
            updatePreview();
        } else {
            showResult('error', '❌ فشل', data.message || data.error || 'خطأ غير معروف');
        }
    } catch(e) {
        showResult('error', '⚠️ خطأ', e.message);
    } finally {
        btn.innerText = original;
        btn.disabled = false;
    }
}

window.addEventListener('load', () => {
    submitBtn.disabled = true;
    submitBtn.textContent = '🔒 تحقق الأول';
});

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// ========== MODYXBIO EXTRAS ==========
const $=id=>document.getElementById(id);
const hx=(h,s,l)=>{l/=100;const a=s*Math.min(l,1-l)/100,f=n=>{const k=(n+h/30)%12;return Math.round(255*(l-a*Math.max(Math.min(k-3,9-k,1),-1))).toString(16).padStart(2,'0')};return '#'+f(0)+f(8)+f(4)};
// ألوان البايو الإضافية
(function(){const ex=['FFFFFF','C0C0C0','808080','404040','000000'];
for(let h=0;h<360;h+=10)ex.push(hx(h,100,50).slice(1));
for(let h=0;h<360;h+=24)ex.push(hx(h,100,75).slice(1),hx(h,100,28).slice(1),hx(h,55,55).slice(1));
ex.forEach(c=>{const d=document.createElement('div');d.className='c-dot';d.style.backgroundColor='#'+c;d.onclick=()=>insertColor(c);ribbon.appendChild(d)});})();
// ثيمات: [خلفية1, خلفية2, أساسي, ثانوي]
const TH=[["#050510","#0b1a2e","#00ffc3","#0099ff"],["#1a0033","#4b0082","#ff00ea","#7b2ff7"],["#2b0000","#7a0000","#ff4d4d","#ff9a00"],["#001f3f","#0057b8","#7fdbff","#00ffc3"],
["#0a2e0a","#145a14","#39ff14","#00e676"],["#2e1a00","#8a4b00","#ffb300","#ff6d00"],["#1b0a2e","#005f73","#ff6ec7","#00e5ff"],["#000000","#1c1c1c","#ffffff","#9e9e9e"],
["#3a0ca3","#f72585","#ffd60a","#4cc9f0"],["#003d33","#00a896","#02c39a","#f0f3bd"],["#42032c","#d7385e","#ffd1dc","#ff5d8f"],["#0f2027","#2c5364","#00e5ff","#76ff03"],
["#ff512f","#dd2476","#fff1a8","#ff9a9e"],["#134e5e","#71b280","#e0ffcf","#00c9a7"],["#232526","#414345","#ff9100","#ffea00"],["#4b134f","#c94b4b","#ffd3a5","#fd6585"],
["#0575e6","#021b79","#00f2fe","#4facfe"],["#f12711","#f5af19","#ffffff","#fff200"]];
function onC(a,b){const L=h=>{h=String(h).replace('#','');if(h.length<6)return .5;const c=[0,2,4].map(i=>{let v=parseInt(h.substr(i,2),16)/255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*c[0]+.7152*c[1]+.0722*c[2]};return (L(a)+L(b))/2>.32?'#000':'#fff'}
function applyT(b1,b2,a,a2,tc){const r=document.documentElement.style;r.setProperty('--b1',b1);r.setProperty('--b2',b2);r.setProperty('--a',a);r.setProperty('--a2',a2);
tc=tc||a;{const oc=onC(a,a2);r.setProperty('--on',oc);r.setProperty('--bm',oc==='#fff'?'82%':'100%')}$('themeColorMeta').content=tc;$('c1').value=b1;$('c2').value=b2;$('c3').value=a;$('c5').value=a2;$('c4').value=tc;
try{localStorage.setItem('mx_theme',JSON.stringify([b1,b2,a,a2,tc]))}catch(e){}}
TH.forEach(t=>{const d=document.createElement('div');d.className='th';d.style.background='linear-gradient(135deg,'+t[0]+','+t[1]+','+t[2]+')';
d.onclick=()=>{document.querySelectorAll('.th').forEach(x=>x.classList.remove('on'));d.classList.add('on');stopRainbow();applyT(...t)};$('themes').appendChild(d)});
['c1','c2','c3','c5','c4'].forEach(id=>$(id).addEventListener('input',()=>applyT($('c1').value,$('c2').value,$('c3').value,$('c5').value,$('c4').value)));
function randomTheme(){stopRainbow();const h=Math.random()*360;applyT(hx(h,70,6),hx((h+40)%360,60,16),hx((h+180)%360,100,60),hx((h+220)%360,100,60))}
let rb=null,hue=0;function stopRainbow(){if(rb){clearInterval(rb);rb=null;$('rbBtn').style.opacity=1}}
function toggleRainbow(){if(rb)return stopRainbow();$('rbBtn').style.opacity=.6;rb=setInterval(()=>{hue=(hue+2)%360;const a=hx(hue,100,60);const r=document.documentElement.style;
r.setProperty('--a',a);r.setProperty('--a2',hx((hue+60)%360,100,60));r.setProperty('--b1',hx(hue,60,6));r.setProperty('--b2',hx((hue+30)%360,55,15));r.setProperty('--on','#000');r.setProperty('--bm','100%');$('themeColorMeta').content=a},60)}
try{const sv=JSON.parse(localStorage.getItem('mx_theme'));sv?applyT(...sv):applyT(...TH[0])}catch(e){applyT(...TH[0])}
// الموسيقى + المؤثر الصوتي
const bgm=$('bgm');bgm.volume=.75;let ac,an,dt,off=false;
function icon(){$('mi').className='fas '+((bgm.paused)?'fa-volume-xmark':'fa-volume-high')}
function viz(){const c=$('viz'),x=c.getContext('2d');(function f(){requestAnimationFrame(f);x.clearRect(0,0,c.width,c.height);if(!an||bgm.paused)return;an.getByteFrequencyData(dt);
const n=16,w=c.width/n;x.fillStyle=getComputedStyle(document.documentElement).getPropertyValue('--a').trim();for(let i=0;i<n;i++){const h=dt[i]/255*c.height;x.fillRect(i*w+2,c.height-h,w-5,h)}})()}
function startMusic(){try{if(!ac){ac=new(window.AudioContext||window.webkitAudioContext)();const s=ac.createMediaElementSource(bgm);an=ac.createAnalyser();an.fftSize=64;s.connect(an);an.connect(ac.destination);dt=new Uint8Array(an.frequencyBinCount);viz()}ac.resume()}catch(e){}
bgm.play().then(icon).catch(icon)}
function toggleMusic(){if(bgm.paused){off=false;startMusic()}else{off=true;bgm.pause();icon()}}
bgm.play().then(icon).catch(()=>{const once=()=>{if(!off)startMusic();['click','touchstart','keydown'].forEach(e=>removeEventListener(e,once))};['click','touchstart','keydown'].forEach(e=>addEventListener(e,once));icon()});
$('enterBtn').onclick=()=>{startMusic();$('welcome').style.display='none'};
// خلفية: كرات مضيئة
for(let i=0;i<2;i++){const o=document.createElement('div');o.className='orb';const z=180+Math.random()*200;o.style.cssText='width:'+z+'px;height:'+z+'px;left:'+Math.random()*60+'vw;top:'+Math.random()*60+'vh;animation-duration:'+(14+Math.random()*14)+'s;animation-delay:-'+Math.random()*10+'s';document.body.appendChild(o)}
// أثر المؤشر
let lt=0;if(matchMedia('(hover:hover)').matches)addEventListener('pointermove',e=>{const n=Date.now();if(n-lt<40)return;lt=n;const d=document.createElement('div');d.className='tr';d.style.left=e.clientX-4+'px';d.style.top=e.clientY-4+'px';document.body.appendChild(d);
d.animate([{opacity:.9,transform:'scale(1)'},{opacity:0,transform:'scale(.2) translateY(14px)'}],{duration:600}).onfinish=()=>d.remove()});
// ميلان 3D للكروت
if(matchMedia('(hover:hover)').matches)document.querySelectorAll('.card').forEach(c=>{c.addEventListener('mousemove',e=>{const r=c.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;c.style.transform='perspective(800px) rotateY('+x*6+'deg) rotateX('+-y*6+'deg)'});c.addEventListener('mouseleave',()=>c.style.transform='')});
// كونفيتي عند النجاح
function confetti(){const cl=['#fff',getComputedStyle(document.documentElement).getPropertyValue('--a').trim(),getComputedStyle(document.documentElement).getPropertyValue('--a2').trim(),'#ffd60a','#ff4d6d'];
for(let i=0;i<70;i++){const d=document.createElement('div');d.className='cf';d.style.left=Math.random()*100+'vw';d.style.background=cl[i%cl.length];document.body.appendChild(d);
d.animate([{transform:'translateY(0) rotate(0)',opacity:1},{transform:'translateY(105vh) rotate('+(360+Math.random()*540)+'deg)',opacity:.8}],{duration:1800+Math.random()*1800,delay:Math.random()*500}).onfinish=()=>d.remove()}}
const _sr=showResult;showResult=function(t,a,b){_sr(t,a,b);if(t==='success')confetti()};

// ========== TOKYO NEON + FEATURES ==========
const rnd=(a,b)=>a+Math.random()*(b-a);
const sc=document.createElement('div');sc.id='scene';document.body.prepend(sc);
(function(){let b='<defs></defs><circle cx="740" cy="140" r="150" fill="var(--a2)" opacity=".16"/><circle cx="740" cy="140" r="80" fill="var(--a2)" opacity=".6"/>';
for(let L=0;L<2;L++){for(let i=0;i<18;i++){const w=rnd(40,80),h=rnd(L?150:220,L?330:470),x=i*58-10;b+='<rect x="'+x+'" y="'+(600-h)+'" width="'+w+'" height="'+h+'" fill="'+(L?'#0d0d24':'#07071a')+'" opacity="'+(L?1:.9)+'"/>';
if(L)for(let k=0;k<h/20;k++)if(Math.random()>.5)b+='<rect class="win" style="animation-delay:-'+rnd(0,7).toFixed(1)+'s" x="'+(x+rnd(6,w-14))+'" y="'+(600-h+k*20+6)+'" width="7" height="9" fill="'+(Math.random()>.5?'var(--a)':'#ffd23f')+'"/>'}}
const sg=(x,y,w,h,t,c,n)=>'<g class="neon '+n+'" style="color:'+c+'"><rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="6" fill="rgba(0,0,0,.4)" stroke="currentColor" stroke-width="3"/><text x="'+(x+w/2)+'" y="'+(y+h/2+7)+'" text-anchor="middle" fill="currentColor" font-size="'+Math.min(22,h*.5)+'" font-weight="900" font-family="Cairo,Arial">'+t+'</text></g>';
b+=sg(60,250,190,44,'MODYXBIO','var(--a)','')+sg(300,300,130,38,'RAMEN 24H','var(--a2)','n2')+sg(560,230,110,36,'ME • EGYPT','#ffd23f','n3')+sg(790,300,150,40,'NEON BAR','var(--a2)','')+sg(430,200,90,32,'ZAATAR','var(--a)','n2');
b+='<g class="neon n3" style="color:var(--a2)"><rect x="965" y="150" width="14" height="170" rx="7" fill="currentColor"/></g><g class="neon n2" style="color:var(--a)"><rect x="25" y="140" width="12" height="150" rx="6" fill="currentColor"/></g>';
b+='<rect x="0" y="560" width="1000" height="40" fill="url(#rf)"/><linearGradient id="rf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--a2)" stop-opacity=".45"/><stop offset="1" stop-color="#000" stop-opacity=".9"/></linearGradient>';
for(let i=0;i<14;i++)b+='<line x1="'+rnd(0,1000)+'" y1="'+rnd(565,595)+'" x2="'+rnd(0,1000)+'" y2="'+rnd(565,595)+'" stroke="var(--a)" stroke-width="1" opacity=".3"/>';
sc.innerHTML='<svg viewBox="0 0 1000 600" preserveAspectRatio="xMidYMax slice">'+b+'</svg>'})();
// مطر قوي + برق
const rc=document.createElement('canvas');rc.id='rain';document.body.prepend(rc);const rx=rc.getContext('2d');let dr=[],flash=0,rcol='#0ff',fc=0;
function rs(){rc.width=innerWidth;rc.height=innerHeight;dr=Array.from({length:Math.min(170,Math.floor(innerWidth/5))},()=>({x:Math.random()*rc.width,y:Math.random()*rc.height,l:rnd(14,34),v:rnd(30,52)}))}rs();addEventListener('resize',rs);
let _rf=0;(function rd(){requestAnimationFrame(rd);if((_rf++&1)||document.hidden||document.body.classList.contains('lite'))return;if(fc++%20===0)rcol=getComputedStyle(document.documentElement).getPropertyValue('--a').trim()||'#0ff';
rx.clearRect(0,0,rc.width,rc.height);rx.strokeStyle=rcol;rx.globalAlpha=.5;rx.lineWidth=1.4;rx.beginPath();
dr.forEach(d=>{rx.moveTo(d.x,d.y);rx.lineTo(d.x-d.l*.25,d.y+d.l);d.y+=d.v;d.x-=d.v*.25;if(d.y>rc.height){d.y=-40;d.x=Math.random()*(rc.width+250)}});rx.stroke();
if(flash>0){rx.globalAlpha=flash;rx.fillStyle='#fff';rx.fillRect(0,0,rc.width,rc.height);flash-=.05}else if(Math.random()<.0007)flash=.3})();
// الثيم الافتراضي = طوكيو نيون
TH[0]=["#050506","#14060a","#ff2b2b","#a8001a"];
try{if(localStorage.getItem('mx_v')!=='4'){applyT(...TH[0]);localStorage.setItem('mx_v','4')}}catch(e){}
// شاشة التحميل
(function(){const m=['جاري تحميل الموقع...','تجهيز الأدوات...','تحميل الموسيقى...','تشغيل نظام الحماية...','جاهز 🚀'];let p=0;const iv=setInterval(()=>{p+=Math.random()*16+10;if(p>=100){p=100;clearInterval(iv);setTimeout(()=>{$('loader').classList.add('off');setTimeout(()=>$('loader').remove(),800)},300)}
$('lfill').style.width=p+'%';$('lpct').textContent=Math.floor(p)+'%';$('ltxt').textContent=m[Math.min(4,Math.floor(p/21))]},70)})();
// شريط الإعلانات (عدّل القائمة دي بإعلاناتك)
const ADS=[['📢 تابعني على تيك توك @king_burd','https://www.tiktok.com/@king_burd'],['✈️ تليجرام المطور @MODYXBOT1','https://t.me/MODYXBOT1'],['💬 واتساب: 01204564384','https://wa.me/201204564384'],['🔥 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 - الأقوى في الشرق الأوسط 🇪🇬','#'],['𝑫𝒆𝒗: 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅 • 𝑭𝑴𝑺: 𝒁𝑨𝑨𝑻𝑨𝑹','#']];
(function(){const h=ADS.map(a=>'<a href="'+a[1]+'" target="_blank" rel="noopener">'+a[0]+'</a><span>✦</span>').join('');$('tk').innerHTML=h+h+h+h})();
// أدوات
const LS={get(k,d){try{return JSON.parse(localStorage.getItem(k))||d}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
const esc=t=>String(t).replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
function bioHtml(raw){const t=esc(raw);let o='',c=null,b=0,i=0,u=0,s=0,p=0;while(p<t.length){if(t[p]==='['){const e=t.indexOf(']',p);if(e>0){const g=t.slice(p+1,e);
if(/^[0-9A-Fa-f]{6}$/.test(g)){c=g;p=e+1;continue}if(g.length===1&&'bicus'.includes(g)){if(g==='b')b=!b;if(g==='i'||g==='c')i=!i;if(g==='u')u=!u;if(g==='s')s=!s;p=e+1;continue}}}
let st='';if(c)st+='color:#'+c+';';if(b)st+='font-weight:bold;';if(i)st+='font-style:italic;';if(u)st+='text-decoration:underline;';if(s)st+='text-decoration:line-through;';o+='<span style="'+st+'">'+t[p]+'</span>';p++}return o}
function toast(m){const d=document.createElement('div');d.className='toast';d.textContent=m;document.body.appendChild(d);setTimeout(()=>d.remove(),1800)}
function copyBio(v){if(!v)return toast('اكتب البايو الأول');const ok=()=>toast('✅ تم النسخ');if(navigator.clipboard)navigator.clipboard.writeText(v).then(ok).catch(()=>fb(v,ok));else fb(v,ok)}
function fb(v,ok){const t=document.createElement('textarea');t.value=v;document.body.appendChild(t);t.select();try{document.execCommand('copy');ok()}catch(e){}t.remove()}
function shareBio(){const v=$('bio').value;if(!v)return toast('اكتب البايو الأول');if(navigator.share)navigator.share({title:'MODYXBIO',text:v,url:location.href}).catch(()=>{});else copyBio(v)}
function useBio(v){$('bio').value=v;$('bio').dispatchEvent(new Event('input'));scrollTo({top:0,behavior:'smooth'});toast('✅ تم الاستخدام')}
function saveBio(){const v=$('bio').value.trim();if(!v)return toast('اكتب البايو الأول');const l=LS.get('mx_saved',[]);l.unshift({t:Date.now(),bio:v});LS.set('mx_saved',l.slice(0,30));renderSaved();toast('💾 تم الحفظ')}
function useSaved(i){useBio(LS.get('mx_saved',[])[i].bio)}
function copySaved(i){copyBio(LS.get('mx_saved',[])[i].bio)}
function useHist(i){useBio(LS.get('mx_hist',[])[i].bio)}
function delSaved(i){const l=LS.get('mx_saved',[]);l.splice(i,1);LS.set('mx_saved',l);renderSaved()}
function renderSaved(){const l=LS.get('mx_saved',[]);$('savedList').innerHTML=l.length?l.map((x,i)=>'<div class="item"><small>'+new Date(x.t).toLocaleString('ar-EG')+'</small>'+bioHtml(x.bio)+'<br><button onclick="useSaved('+i+')">استخدام</button><button onclick="copySaved('+i+')">نسخ</button><button onclick="delSaved('+i+')">حذف</button></div>').join(''):'<div class="item">مفيش بايوهات محفوظة لسه — اكتب بايو واضغط 💾 حفظ</div>'}
function renderHist(){const l=LS.get('mx_hist',[]);$('stM').textContent=l.filter(x=>x.ok).length;$('histList').innerHTML=l.length?l.map((x,i)=>'<div class="item"><small>'+(x.ok?'✅':'❌')+' '+new Date(x.t).toLocaleString('ar-EG')+(x.name?' • '+esc(x.name):'')+(x.uid?' • '+esc(x.uid):'')+'</small>'+bioHtml(x.bio||'')+(x.msg?'<div style="color:#ff7b7b">'+esc(x.msg)+'</div>':'')+'<br><button onclick="useHist('+i+')">إعادة استخدام</button></div>').join(''):'<div class="item">السجل فاضي</div>'}
function clearHist(){LS.set('mx_hist',[]);renderHist()}
const _sr2=showResult;showResult=function(t,a,b){try{const d=document.createElement('div');d.innerHTML=b;const x=d.textContent;let uid='',name='';
if(x.includes('UID:')){uid=x.split('UID:')[1].split('👤')[0].trim();name=(x.split('الاسم:')[1]||'').split('🌍')[0].trim()}
const h=LS.get('mx_hist',[]);h.unshift({t:Date.now(),bio:$('bio').value,ok:t==='success',uid:uid,name:name,msg:t==='success'?'':x.slice(0,80)});LS.set('mx_hist',h.slice(0,30));renderHist()}catch(e){}_sr2(t,a,b)};
// قوالب
const TP=[['👑 ملك','[FFD700][b]👑 KING [FFFFFF]| [FFD700]𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 [FFFFFF]👑'],['🔥 نار','[FF3B30][b]🔥 𝑭𝑰𝑹𝑬 [FF9500]𝑴𝑶𝑫𝑬 [FFD60A]🔥'],['🇪🇬 مصري','[FFFFFF][b]🇪🇬 [E4002B]مصري [FFFFFF]وأفتخر [FFD700]🇪🇬'],['❄️ ثلج','[00E5FF][b]❄️ 𝑰𝑪𝑬 [FFFFFF]𝑲𝑰𝑵𝑮 [00E5FF]❄️'],['💎 ألماس','[00FFFF][b]💎 𝑫𝑰𝑨𝑴𝑶𝑵𝑫 [FF2BD6]𝑷𝑳𝑨𝒀𝑬𝑹 [00FFFF]💎'],['🌈 قوس قزح','[b][FF0000]R[FF7F00]A[FFFF00]I[00FF00]N[00BFFF]B[8B00FF]O[FF00FF]W'],['⚡ نيون','[00F0FF][b]⚡ NEON [FF2BD6]TOKYO [00F0FF]⚡'],['🖤 غامض','[808080][i]الظلام [FFFFFF][b]مش بيخوفني [808080][i]أنا اللي فيه'],['🎮 جيمر','[39FF14][b]🎮 PRO GAMER [FFFFFF]| [39FF14]No Mercy'],['😎 كول','[FFFFFF][b]😎 Cool [C0C0C0]& [FFFFFF]Legend']];
TP.forEach(p=>{const b=document.createElement('button');b.className='format-btn';b.textContent=p[0];b.onclick=()=>useBio(p[1]);$('tpls').appendChild(b)});
// إحصائيات
function countUp(el,to){let c=0;const st=Math.max(1,Math.ceil(to/40));const iv=setInterval(()=>{c=Math.min(to,c+st);el.textContent=c;if(c>=to)clearInterval(iv)},30)}
(async function(){try{let first=false;try{first=!sessionStorage.getItem('mx_seen');sessionStorage.setItem('mx_seen','1')}catch(e){}
const r=await fetch(first?'/api/visit':'/api/stats',{method:first?'POST':'GET'});const d=await r.json();countUp($('stV'),d.visits||0);countUp($('stU'),d.updates||0)}catch(e){}})();
renderSaved();renderHist();

// ========== v5: لغة / تقييم / دفتر زوار / مشاركة / رسالة / لوحة مطور ==========
const NL=String.fromCharCode(10);
const EN_RAW=`حمّل تطبيق 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶|Get the 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 app
⚡ سريع|⚡ Fast
🛡️ آمن|🛡️ Secure
♾️ مجاني|♾️ Free
⭐ متاح 24/7|⭐ Available 24/7
🤖 تواصل تليجرام|🤖 Telegram admin
📲 تثبيت التطبيق|📲 Install the app
⬇️ تحميل APK|⬇️ Download APK
أندرويد|Android
آيفون|iPhone
افتح الموقع في كروم|Open the site in Chrome
اضغط ⋮ ثم «تثبيت التطبيق»|Tap ⋮ then "Install app"
افتحه من الشاشة الرئيسية|Open it from your home screen
افتح الموقع في سفاري|Open the site in Safari
اضغط زر المشاركة ⬆️|Tap the Share button ⬆️
اختر «إضافة إلى الشاشة الرئيسية»|Choose "Add to Home Screen"
مجاني|Free
كل المميزات بدون اشتراك ولا مقابل.|All features, no subscription, no fees.
متاح 24/7|Available 24/7
الموقع شغال طول اليوم من أي مكان.|The site runs all day, from anywhere.
اللهم صلِّ وسلِّم على سيدنا محمد ﷺ|May Allah send peace and blessings upon our Prophet Muhammad ﷺ
أهلاً بك في 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶|Welcome to 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶
تابعني على تيك توك الأول عشان توصلك كل الجديد 🔥|Follow me on TikTok first so you get all the news 🔥
وبعدها اضغط دخول|Then press Enter
صفحتي على تيك توك|My TikTok page
🚀 دخول الموقع|🚀 Enter the site
🔒 التحقق البشري|🔒 Human Verification
أكد إنك إنسان عشان تدخل الأداة|Confirm you are human to access the tool
محمي بنظام أمان متقدم|Protected by advanced security
اسحب للتحقق|Slide to verify
👉 اسحب الزر لليمين|👉 Drag the slider to the right
⟳ تحديث|⟳ Refresh
اتصال آمن|Secure Connection
الجلسة نشطة|Session Active
🔓 كمّل سحب...|🔓 Keep sliding...
✅ تم التحقق بنجاح!|✅ Verified successfully!
✅ تم|✅ Done
👉 اسحب لآخر الشريط|👉 Drag to the end
🔄 تم إعادة التحقق|🔄 Verification reset
تليجرام|Telegram
تيك توك|TikTok
واتساب|WhatsApp
✏️ محرر البايو|✏️ Bio Editor
معاينة مباشرة|Live Preview
📋 نسخ|📋 Copy
🔗 مشاركة|🔗 Share
💾 حفظ|💾 Save
⚡ قوالب بايو جاهزة (اضغط واستخدم)|⚡ Ready bio templates (tap to use)
👑 ملك|👑 King
🔥 نار|🔥 Fire
🇪🇬 مصري|🇪🇬 Egyptian
❄️ ثلج|❄️ Ice
💎 ألماس|💎 Diamond
🌈 قوس قزح|🌈 Rainbow
⚡ نيون|⚡ Neon
🖤 غامض|🖤 Mystery
🎮 جيمر|🎮 Gamer
😎 كول|😎 Cool
🎨 التنسيق|🎨 Formatting
عريض|Bold
مائل|Italic
منحني|Curve
تحته خط|Underline
مشطوب|Strike
🌈 ألوان البايو (كل ألوان العالم)|🌈 Bio colors (all the world's colors)
🎯 لون مخصص من عندك|🎯 Your custom color
🖌️ ألوان الموقع والخلفية|🖌️ Site & background colors
🎨 لون الخلفية الأول|🎨 Background color 1
🎨 لون الخلفية الثاني|🎨 Background color 2
✨ لون الموقع الأساسي|✨ Main site color
💫 لون الموقع الثانوي|💫 Secondary site color
📱 لون شريط المتصفح|📱 Browser bar color
🎲 عشوائي|🎲 Random
↺ الافتراضي|↺ Default
🔐 طريقة الدخول|🔐 Login method
JWT Token (مباشر)|JWT Token (direct)
UID & الباسورد|UID & Password
🇪🇬 ME - الشرق الأوسط (مصر)|🇪🇬 ME - Middle East (Egypt)
🇮🇳 IND - الهند|🇮🇳 IND - India
🇧🇩 BD - بنجلاديش|🇧🇩 BD - Bangladesh
🇸🇬 SG - سنغافورة|🇸🇬 SG - Singapore
🇧🇷 BR - البرازيل|🇧🇷 BR - Brazil
🇺🇸 US - أمريكا|🇺🇸 US - USA
🇪🇺 EU - أوروبا|🇪🇺 EU - Europe
🔒 تحقق الأول|🔒 Verify first
🚀 تحديث البايو|🚀 UPDATE BIO
⏳ جاري التنفيذ...|⏳ Processing...
✅ تم بنجاح!|✅ SUCCESS!
❌ فشل|❌ FAILED
⚠️ خطأ|⚠️ ERROR
👤 الاسم:|👤 Name:
🌍 المنطقة:|🌍 Region:
🔑 الطريقة:|🔑 Method:
تم تحديث البايو بنجاح|Bio updated successfully
خطأ غير معروف|Unknown error
📊 إحصائيات الموقع|📊 Site statistics
👁️ زوار الموقع|👁️ Visitors
✅ تحديثات ناجحة|✅ Successful updates
🙋 تحديثاتك أنت|🙋 Your updates
⭐ قيّم الموقع|⭐ Rate the site
المتوسط:|Average:
💾 بايوهاتي المحفوظة|💾 My saved bios
🕘 سجل التحديثات|🕘 Update history
🗑️ مسح السجل|🗑️ Clear history
استخدام|Use
نسخ|Copy
حذف|Delete
إعادة استخدام|Reuse
السجل فاضي|History is empty
مفيش بايوهات محفوظة لسه — اكتب بايو واضغط 💾 حفظ|No saved bios yet — write a bio and press 💾 Save
📖 دفتر الزوار|📖 Guestbook
📨 إرسال التعليق|📨 Send comment
كن أول من يترك تعليق 💬|Be the first to leave a comment 💬
📣 شارك الموقع|📣 Share the site
✉️ ابعت رسالة للمطور|✉️ Message the developer
في تليجرام وتيك توك الرسالة بتتنسخ تلقائي، والصقها في المحادثة.|On Telegram and TikTok the message is copied automatically — paste it in the chat.
📞 تواصل مع المطور|📞 Contact the developer
جاري التحميل...|Loading...
جاري تحميل الموقع...|Loading the site...
تجهيز الأدوات...|Preparing tools...
تحميل الموسيقى...|Loading music...
تشغيل نظام الحماية...|Starting security system...
جاهز 🚀|Ready 🚀
✅ تم النسخ|✅ Copied
اكتب البايو الأول|Write the bio first
✅ تم الاستخدام|✅ Applied
💾 تم الحفظ|💾 Saved
اكتب رسالتك الأول|Write your message first
اكتب تعليق الأول|Write a comment first
✅ تم إرسال تعليقك|✅ Comment sent
⚠️ حصلت مشكلة|⚠️ Something went wrong
شكراً على تقييمك ⭐|Thanks for your rating ⭐
قيّمت قبل كده ⭐|You already rated ⭐
التوكن مطلوب!|Token required!
اكتب البايو الأول!|Bio is required!
البايو قصير - 3 حروف على الأقل|Bio too short - minimum 3 characters
الباسورد مطلوب!|Password required!
🔐 لوحة المطور|🔐 Developer panel
دخول|Login
📊 ملخص|📊 Summary
💾 حفظ الإعلانات|💾 Save ads
💬 تعليقات الزوار|💬 Visitor comments
♻️ تصفير الإحصائيات|♻️ Reset statistics
إغلاق|Close
📢 إعلانات الشريط (سطر لكل إعلان: النص | الرابط)|📢 Ticker ads (one per line: text | link)
© جميع الحقوق محفوظة — 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 🇪🇬 • 𝑫𝒆𝒗: 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅|© All rights reserved — 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 🇪🇬 • 𝑫𝒆𝒗: 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅
اكتب البايو بتاعك هنا...|Write your bio here...
التوكن / UID|Token / UID
الباسورد|Password
اسمك|Your name
اكتب تعليقك هنا...|Write your comment here...
اسمك (اختياري)|Your name (optional)
اكتب رسالتك...|Write your message...
كلمة السر|Password
📢 تابعني على تيك توك @king_burd|📢 Follow me on TikTok @king_burd
✈️ تليجرام المطور @MODYXBOT1|✈️ Developer Telegram @MODYXBOT1
💬 واتساب: 01204564384|💬 WhatsApp: 01204564384
🔥 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 - الأقوى في الشرق الأوسط 🇪🇬|🔥 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 - The strongest in the Middle East 🇪🇬
🌍 معرض البايوهات العام|🌍 Public bio gallery
🕒 الأحدث|🕒 Newest
🔥 الأكثر إعجاباً|🔥 Most liked
✨ استخدام|✨ Use
نشر البايو في المعرض العام (بيظهر نص البايو بس، من غير توكن أو UID)|Publish the bio to the public gallery (only the bio text is shown — no token or UID)
مفيش بايوهات لسه — كن أول واحد 🚀|No bios yet — be the first 🚀
🌍 المعرض العام|🌍 Public gallery
ليه 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶؟|Why 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶?
🇪🇬 الشرق الأوسط • ME|🇪🇬 Middle East • ME
محرر بايو احترافي بألوان وتنسيقات لا نهائية، وقوالب جاهزة، ومعرض عام تشوف فيه بايوهات الناس وتستخدمها.|A professional bio editor with unlimited colors and formats, ready templates, and a public gallery where you can browse and use other people's bios.
✏️ ابدأ دلوقتي|✏️ Start now
🌍 شوف المعرض|🌍 Browse the gallery
زائر|Visitors
تحديث ناجح|Successful updates
التقييم|Rating
سريع|Fast
حدّث البايو في ثواني من أي جهاز.|Update your bio in seconds from any device.
ألوان لا نهائية|Unlimited colors
أكتر من 100 لون وتنسيقات وقوالب جاهزة.|100+ colors, formats and ready templates.
معرض عام|Public gallery
شوف بايوهات الناس واستخدمها واعمل لايك.|Browse people's bios, use them and like them.
خصوصيتك|Your privacy
ما بنخزنش التوكن ولا الباسورد عندنا.|We don't store your token or password.
إزاي تستخدمه؟|How to use it?
اختار طريقة الدخول|Pick a login method
اختار نوع التوكن والسيرفر، وحط بياناتك.|Choose the token type and server, then enter your details.
اكتب وزخرف|Write & decorate
اكتب البايو وزوّقه بالألوان أو استخدم قالب جاهز.|Write your bio and color it, or use a ready template.
دوس تحديث|Press update
اتحقق إنك إنسان وادوس تحديث البايو.|Verify you're human and press update.
أسئلة شائعة|FAQ
إيه هو التوكن؟|What is a token?
مفتاح دخول مؤقت للحساب، بيستخدمه الموقع عشان يحدّث البايو. ما بنحفظهوش عندنا.|A temporary account key the site uses to update your bio. We don't save it.
ليه التحقق البشري؟|Why the human check?
عشان نحمي الموقع من الروبوتات والضغط الزايد.|To protect the site from bots and overload.
البايو بتاعي بيظهر لمين؟|Who can see my bio?
لو سبت علامة النشر مفعّلة، نص البايو بس بيظهر في المعرض العام، من غير أي بيانات حساب.|If you keep publishing on, only the bio text appears in the public gallery, with no account data.
لو حصلت مشكلة أكلم مين؟|Who do I contact if there's a problem?
كلّم المطور على تليجرام @MODYXBOT1 أو واتساب 01204564384.|Contact the developer on Telegram @MODYXBOT1 or WhatsApp 01204564384.
محرر بايو للشرق الأوسط 🇪🇬|Bio editor for the Middle East 🇪🇬
روابط|Links
المحرر|Editor
المعرض|Gallery
الألوان|Colors
كيف يعمل|How it works
الأسئلة|FAQ
تواصل|Contact
🎨 اختار مزاجك|🎨 Pick your mood
🔤 مولد الخطوط والزخرفة|🔤 Font & style generator
🌈 تدرج لوني للنص|🌈 Text color gradient
✨ مكتبة الرموز|✨ Symbols library
🖼️ البايو كصورة|🖼️ Bio as image
🎵 مشغل الموسيقى|🎵 Music player
اكتب اسمك بالإنجليزي|Type your name in English
🎨 من|🎨 From
إلى|To
كل كام حرف|Every N letters
🌈 طبّق التدرج على البايو|🌈 Apply gradient to bio
🖼️ إنشاء الصورة|🖼️ Create image
📤 مشاركة الصورة|📤 Share image
🔊 الصوت|🔊 Volume
🎧 أغنية من جهازك|🎧 Song from your device
↺ الأغنية الأساسية|↺ Default song
⏯ تشغيل / إيقاف|⏯ Play / Pause
⬇️ تصدير|⬇️ Export
⬆️ استيراد|⬆️ Import
⚡ وضع الأداء|⚡ Performance mode
📲 ثبّت التطبيق|📲 Install app
🧭 جولة|🧭 Tour
التالي ▶|Next ▶
تخطي|Skip
✏️ اكتب بايوك هنا وزوّقه بالألوان والقوالب والخطوط|✏️ Write your bio here and style it with colors, templates and fonts
🎨 غيّر ألوان الموقع كلها من هنا أو من زرار 🎨 العايم|🎨 Change the whole site's colors here or with the floating 🎨 button
🌍 شوف بايوهات الناس واستخدمها واعمل لايك ❤️|🌍 Browse people's bios, use them and like them ❤️
📞 أي استفسار؟ كلّم المطور|📞 Any question? Contact the developer
استنى ثواني قبل التحديث الجاي ⏳|Wait a few seconds before the next update ⏳
التدرج طويل — قصّر النص أو زوّد كل كام حرف|Gradient too long — shorten the text or raise the step
✅ تم تطبيق التدرج|✅ Gradient applied
✅ تم الاستيراد|✅ Imported
اعمل التقييم من ⋮ ثم "إضافة للشاشة الرئيسية"|Use ⋮ then "Add to Home screen"
📲 حمّل تطبيق 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶|📲 Get the 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 app
ثبّته على موبايلك وافتحه بضغطة زي أي تطبيق، سريع وبملء الشاشة.|Install it on your phone and open it in one tap like any app — fast and full-screen.
📲 تثبيت التطبيق|📲 Install app
⬇️ تحميل APK|⬇️ Download APK
تمام|OK
✅ التطبيق مثبّت عندك|✅ The app is installed
📲 على iPhone: اضغط زرار المشاركة ⬆️ في Safari ثم "إضافة إلى الشاشة الرئيسية"|📲 On iPhone: tap the Share button ⬆️ in Safari, then "Add to Home Screen"
📲 على أندرويد: اضغط ⋮ في المتصفح ثم "تثبيت التطبيق" أو "إضافة إلى الشاشة الرئيسية"|📲 On Android: tap ⋮ in your browser, then "Install app" or "Add to Home screen"`;
const EN={};EN_RAW.split(NL).forEach(l=>{const i=l.indexOf('|');if(i>0)EN[l.slice(0,i)]=l.slice(i+1)});
let LANG='ar';try{LANG=localStorage.getItem('mx_lang')||'ar'}catch(e){}
const orig=new WeakMap();
function trNode(n){const t=n.nodeValue.trim();if(!t)return;if(LANG==='en'){const e=EN[t];if(e){if(!orig.has(n))orig.set(n,n.nodeValue);n.nodeValue=n.nodeValue.replace(t,e)}}else if(orig.has(n)){n.nodeValue=orig.get(n);orig.delete(n)}}
function trAll(root){const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>['SCRIPT','STYLE','TEXTAREA'].includes(n.parentNode.nodeName)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});const a=[];let n;while(n=w.nextNode())a.push(n);a.forEach(trNode)}
function trAttrs(){document.querySelectorAll('[placeholder]').forEach(e=>{if(!e.dataset.pa)e.dataset.pa=e.placeholder;e.placeholder=LANG==='en'?(EN[e.dataset.pa]||e.dataset.pa):e.dataset.pa})}
function setLang(l){LANG=l;try{localStorage.setItem('mx_lang',l)}catch(e){}document.documentElement.lang=l;document.documentElement.dir=l==='en'?'ltr':'rtl';
document.title=l==='en'?'MODYXBIO | Bio Editor - Middle East ME':'MODYXBIO | محرر البايو - الشرق الأوسط ME';$('langBtn').textContent=l==='en'?'🌐 عربي':'🌐 EN';trAll(document.body);trAttrs()}
function toggleLang(){setLang(LANG==='en'?'ar':'en')}
new MutationObserver(ms=>{if(LANG!=='en')return;ms.forEach(m=>{if(m.type==='characterData')trNode(m.target);else m.addedNodes.forEach(n=>{if(n.nodeType===3)trNode(n);else if(n.nodeType===1){trAll(n);n.querySelectorAll&&n.querySelectorAll('[placeholder]').length&&trAttrs()}})})}).observe(document.body,{childList:true,subtree:true,characterData:true});
const _al=window.alert;window.alert=m=>_al(LANG==='en'?(EN[m]||m):m);
// ---- شريط الإعلانات من لوحة المطور ----
function buildTk(){const h=ADS.map(a=>'<a href="'+esc(fx(a[1]))+'" target="_blank" rel="noopener">'+esc(fx(a[0]))+'</a><span>✦</span>').join('');$('tk').innerHTML=h+h+h+h}
fetch('/api/ads').then(r=>r.json()).then(l=>{if(l&&l.length){ADS.length=0;l.forEach(a=>ADS.push(a));buildTk()}}).catch(()=>{});
// ---- تقييم ----
let myRate=LS.get('mx_rate',0);
function drawStars(n){[...$('stars').children].forEach((s,i)=>s.classList.toggle('on',i<n))}
for(let i=1;i<=5;i++){const sp=document.createElement('span');sp.textContent='★';sp.onmouseenter=()=>drawStars(i);sp.onmouseleave=()=>drawStars(myRate);sp.onclick=()=>rate(i);$('stars').appendChild(sp)}drawStars(myRate);
function showAvg(d){const n=d.rate_n||0;$('avg').textContent=n?(d.rate_sum/n).toFixed(1)+' / 5 ('+n+')':'—'}
async function rate(n){if(myRate)return toast('قيّمت قبل كده ⭐');try{const r=await fetch('/api/rate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({stars:n})});const d=await r.json();if(d.error)return toast(d.error);myRate=n;LS.set('mx_rate',n);drawStars(n);showAvg(d);toast('شكراً على تقييمك ⭐')}catch(e){toast('⚠️ حصلت مشكلة')}}
fetch('/api/stats').then(r=>r.json()).then(showAvg).catch(()=>{});
// ---- دفتر الزوار ----
function renderGb(l){$('gbList').innerHTML=l.length?l.map(x=>'<div class="item"><small>'+esc(x.name)+' • '+new Date(x.t).toLocaleString(LANG==='en'?'en-GB':'ar-EG')+'</small>'+esc(x.text)+'</div>').join(''):'<div class="item">كن أول من يترك تعليق 💬</div>'}
fetch('/api/guest').then(r=>r.json()).then(d=>renderGb(d.list||[])).catch(()=>{});
async function gbSend(){const name=$('gbName').value.trim()||'زائر',text=$('gbText').value.trim();if(text.length<2)return toast('اكتب تعليق الأول');try{const r=await fetch('/api/guest',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,text:text})});const d=await r.json();if(d.error)return toast(d.error);$('gbText').value='';renderGb(d.list);toast('✅ تم إرسال تعليقك')}catch(e){toast('⚠️ حصلت مشكلة')}}
// ---- مشاركة ----
const enc=encodeURIComponent;
function shareTxt(){return LANG==='en'?'Try MODYXBIO - the best bio editor 🔥':'جرب 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 - أقوى موقع لتغيير البايو 🔥'}
[['WhatsApp','fa-whatsapp','#25D366',u=>'https://wa.me/?text='+enc(shareTxt()+' '+u)],['Telegram','fa-telegram','#229ED9',u=>'https://t.me/share/url?url='+enc(u)+'&text='+enc(shareTxt())],['X','fa-x-twitter','#000',u=>'https://twitter.com/intent/tweet?text='+enc(shareTxt())+'&url='+enc(u)],['Facebook','fa-facebook','#1877F2',u=>'https://www.facebook.com/sharer/sharer.php?u='+enc(u)]].forEach(p=>{const a=document.createElement('a');a.className='sb';a.style.background=p[2];a.target='_blank';a.rel='noopener';a.href=p[3](location.href);a.innerHTML='<i class="fab '+p[1]+'"></i> '+p[0];$('shr').appendChild(a)});
const cb=document.createElement('button');cb.className='sb';cb.style.background='#555';cb.innerHTML='<i class="fas fa-link"></i> '+'Link';cb.onclick=()=>copyBio(location.href);$('shr').appendChild(cb);
// ---- رسالة للمطور ----
function msgTo(k){const n=$('mName').value.trim(),m=$('mText').value.trim();if(!m)return toast('اكتب رسالتك الأول');const full=(n?n+': ':'')+m;
if(k==='wa'){open('https://wa.me/'+CT.wa+'?text='+enc(full),'_blank')}else{open(k==='tg'?'https://t.me/'+CT.tg:'https://www.tiktok.com/@'+CT.tt,'_blank');copyBio(full)}}
// ---- لوحة المطور ----
let TOK='';try{TOK=sessionStorage.getItem('mx_tok')||''}catch(e){}
async function api(p,body){const r=await fetch(p,{method:body?'POST':'GET',headers:{'Content-Type':'application/json','X-Token':TOK},body:body?JSON.stringify(body):undefined});return r.json()}
function admOpen(){$('adm').classList.add('on');admRender()}
function admClose(){$('adm').classList.remove('on')}
async function admLogin(){try{const d=await api('/api/admin/login',{pass:$('admPass').value});if(d.token){TOK=d.token;try{sessionStorage.setItem('mx_tok',TOK)}catch(e){}$('admPass').value='';admRender()}else toast(d.error||'❌ كلمة السر غلط')}catch(e){toast('⚠️ حصلت مشكلة')}}
async function admRender(){let d={error:1};if(TOK){try{d=await api('/api/admin/summary')}catch(e){}}
if(d.error){TOK='';$('admLogin').style.display='block';$('admPanel').style.display='none';return}
$('admLogin').style.display='none';$('admPanel').style.display='block';const s=d.stats||{},n=s.rate_n||0;
$('admStats').innerHTML='👁️ '+(s.visits||0)+' • ✅ '+(s.updates||0)+' • ❌ '+(s.failed||0)+' • ⭐ '+(n?(s.rate_sum/n).toFixed(1):'—')+' ('+n+') • 💬 '+(d.guest||[]).length;
$('admAds').value=(d.ads&&d.ads.length?d.ads:ADS).map(a=>a[0]+' | '+a[1]).join(NL);
$('admGb').innerHTML=(d.guest||[]).map(x=>'<div class="item"><small>'+esc(x.name)+'</small>'+esc(x.text)+'<br><button onclick="admDel('+x.id+')">حذف</button></div>').join('')||'<div class="item">—</div>'}
async function admSaveAds(){const ads=$('admAds').value.split(NL).map(l=>{const i=l.lastIndexOf('|');return i>0?[l.slice(0,i).trim(),l.slice(i+1).trim()]:[l.trim(),'#']}).filter(a=>a[0]);const d=await api('/api/admin/ads',{ads:ads});if(d.ok){ADS.length=0;ads.forEach(a=>ADS.push(a));buildTk();toast('✅ تم الحفظ ('+d.count+')')}else toast('⚠️ حصلت مشكلة')}
async function admDel(id){await api('/api/admin/guest/delete',{id:id});admRender();fetch('/api/guest').then(r=>r.json()).then(d=>renderGb(d.list||[]))}
async function admReset(){if(!confirm('تصفير كل الإحصائيات؟'))return;await api('/api/admin/reset',{});admRender()}
if(LANG==='en')setLang('en');

// ========== المعرض العام ==========
let gSort='new',GAL=[];
function galSort(k){gSort=k;$('tNew').classList.toggle('off',k!=='new');$('tTop').classList.toggle('off',k!=='top');loadGallery()}
async function loadGallery(){try{const r=await fetch('/api/gallery?sort='+gSort);const d=await r.json();GAL=d.list||[];renderGal()}catch(e){}}
function renderGal(){const lk=LS.get('mx_likes',[]);$('galList').innerHTML=GAL.length?GAL.map(x=>{const on=lk.includes(x.id);return '<div class="item">'+bioHtml(x.bio)+'<br><small style="margin-top:6px">🕒 '+new Date(x.t).toLocaleString(LANG==='en'?'en-GB':'ar-EG')+' • ✨ '+(x.uses||0)+'</small><button class="'+(on?'liked':'')+'" onclick="likeG('+x.id+')">'+(on?'❤️':'🤍')+' '+(x.likes||0)+'</button><button onclick="useG('+x.id+')">✨ استخدام</button><button onclick="copyG('+x.id+')">📋 نسخ</button></div>'}).join(''):'<div class="item">مفيش بايوهات لسه — كن أول واحد 🚀</div>'}
async function likeG(id){const lk=LS.get('mx_likes',[]);if(lk.includes(id))return;try{const r=await fetch('/api/gallery/like',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})});const d=await r.json();if(d.error)return;lk.push(id);LS.set('mx_likes',lk);const x=GAL.find(g=>g.id===id);if(x)x.likes=d.likes;renderGal()}catch(e){toast('⚠️ حصلت مشكلة')}}
function useG(id){const x=GAL.find(g=>g.id===id);if(!x)return;useBio(x.bio);fetch('/api/gallery/use',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})}).catch(()=>{})}
function copyG(id){const x=GAL.find(g=>g.id===id);if(x)copyBio(x.bio)}
loadGallery();setInterval(loadGallery,60000);
const _sr3=showResult;showResult=function(t,a,b){_sr3(t,a,b);if(t==='success')setTimeout(loadGallery,900)};
// إدارة المعرض من لوحة المطور
async function admDelG(id){await api('/api/admin/gallery/delete',{id:id});admRender();loadGallery()}
const _ar=admRender;admRender=async function(){await _ar();if(!TOK)return;try{const d=await api('/api/admin/summary');$('admGal').innerHTML=(d.gallery||[]).map(x=>'<div class="item">'+bioHtml(x.bio)+'<small>❤️ '+(x.likes||0)+' • ✨ '+(x.uses||0)+'</small><button onclick="admDelG('+x.id+')">حذف</button></div>').join('')||'<div class="item">—</div>'}catch(e){}};

// ========== v6: تصميم ==========
(function(){
 const svg=sc.querySelector('svg');
 if(svg){let c='';const cl=['var(--a)','#ffffff','#ff3b30','var(--a2)','#ffd23f'];for(let i=0;i<10;i++){const y=566+Math.random()*24,l=30+Math.random()*50,d=3+Math.random()*5;c+='<line class="car" style="animation-duration:'+d+'s;animation-delay:-'+(Math.random()*d).toFixed(1)+'s" x1="0" y1="'+y+'" x2="'+l+'" y2="'+y+'" stroke="'+cl[i%5]+'" stroke-width="'+(2+Math.random()*2)+'" stroke-linecap="round"/>'}svg.insertAdjacentHTML('beforeend','<g style="filter:drop-shadow(0 0 6px #fff)">'+c+'</g>')}
 // آلة كاتبة
 const PH={ar:['أقوى محرر بايو في الشرق الأوسط 🇪🇬','ألوان بلا حدود 🌈','معرض بايوهات عام ❤️','اكتب بايو يخطف الأنظار ⚡'],en:['The strongest bio editor in the Middle East 🇪🇬','Unlimited colors 🌈','Public bio gallery ❤️','Write a bio that stands out ⚡']};
 let pi=0,ci=0,del=false;
 (function tw(){const L=PH[LANG==='en'?'en':'ar'],a=Array.from(L[pi%L.length]),el=$('tw');
  if(!del){ci++;el.textContent=a.slice(0,ci).join('');if(ci>=a.length){del=true;return setTimeout(tw,1700)}}
  else{ci--;el.textContent=a.slice(0,ci).join('');if(ci<=0){del=false;pi++}}
  setTimeout(tw,del?35:70)})();
 // شريط تنقل سفلي
 const NV=[['✏️','secEd'],['🌍','secGal'],['🎨','secCol'],['💬','secGb'],['📞','secCt']];
 const nv=document.createElement('div');nv.id='nav';
 NV.forEach(n=>{const b=document.createElement('button');b.textContent=n[0];b.dataset.t=n[1];b.onclick=()=>{const t=$(n[1]);if(t)t.scrollIntoView({behavior:'smooth',block:'start'})};nv.appendChild(b)});
 document.body.appendChild(nv);
 if('IntersectionObserver' in window){
  const io2=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)nv.querySelectorAll('button').forEach(b=>b.classList.toggle('on',b.dataset.t===e.target.id))}),{rootMargin:'-35% 0px -55% 0px'});
  NV.forEach(n=>{const t=$(n[1]);if(t)io2.observe(t)});
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.06});
  document.querySelectorAll('.card').forEach(c=>{c.classList.add('rv');io.observe(c)});
 }
 // بارالاكس للمدينة
 let px=0,py=0,q=false;
 addEventListener('pointermove',e=>{px=e.clientX/innerWidth-.5;py=e.clientY/innerHeight-.5;if(!q){q=true;requestAnimationFrame(()=>{sc.style.transform='translate('+(-px*18)+'px,'+(-py*10)+'px) scale(1.05)';q=false})}});
 setInterval(()=>$('musicBtn').classList.toggle('playing',!bgm.paused),500);
})();

// ========== v7: موقع حقيقي ==========
(function(){
 const c=document.querySelector('.container'),cs=[...c.children].filter(e=>e.classList.contains('card'));
 if(cs.length>=15){const cols=document.createElement('div'),A=document.createElement('div'),B=document.createElement('div');cols.className='cols';A.className='colA';B.className='colB';c.insertBefore(cols,cs[0]);cols.append(A,B);
  [0,1,2,3,5].forEach(i=>A.appendChild(cs[i]));[6,4,7,8,9,10,11,12,13].forEach(i=>B.appendChild(cs[i]))}
 $('nav2').appendChild($('langBtn'));
 setTimeout(()=>fetch('/api/stats').then(r=>r.json()).then(d=>{$('hV').textContent=d.visits||0;$('hU').textContent=d.updates||0;const n=d.rate_n||0;$('hR').textContent=n?(d.rate_sum/n).toFixed(1)+'★':'—'}).catch(()=>{}),900);
 document.querySelectorAll('.sec,.hero').forEach(e=>{if(!('IntersectionObserver' in window))return;e.classList.add('rv');const o=new IntersectionObserver(es=>{if(es[0].isIntersecting){e.classList.add('in');o.disconnect()}},{threshold:.05});o.observe(e)});
})();

// ========== v8: ألوان ==========
(function(){
 const au=document.createElement('div');au.id='aur';document.body.prepend(au);
 const NT=[['Aurora',"#021a1a","#0b3d4f","#5cffb0","#a78bfa"],['Cyber Pink',"#12001f","#3d0a4f","#ff2bd6","#00f0ff"],['Sunset',"#2b0a3d","#c2185b","#ffb347","#ff6f61"],['Lava',"#1a0500","#7a1200","#ff5a1f","#ffd23f"],
 ['Gold',"#0d0b05","#2b2208","#ffd700","#ffb300"],['Candy',"#2a0a2a","#ff6ec7","#ffe66d","#6ee7ff"],['Galaxy',"#05001a","#2a0a6b","#b388ff","#ff6ec7"],['Mint',"#00130f","#014d3a","#7dffc9","#d4ff7a"],
 ['Blood Moon',"#100000","#4a0000","#ff1744","#ff8a65"],['Toxic',"#050f00","#173300","#aeea00","#00e676"],['Midnight',"#00031a","#0a1f6b","#448aff","#18ffff"],['Ocean Deep',"#00121a","#00406b","#00e5ff","#76ff03"],['Royal Gold',"#0a0805","#2b1d08","#ffd700","#ff9d00"],['Rose Gold',"#1a0a0f","#3d1a24","#f4c2c2","#e8a87c"],['Emerald VIP',"#00110b","#03442e","#50fa7b","#d4af37"],['Platinum',"#0a0a0f","#262633","#e5e4e2","#9aa0c4"]];
 NT.forEach(n=>TH.push(n.slice(1)));
 function sw(t,name,host){const d=document.createElement('div');d.className='th';d.title=name||'';d.style.background='linear-gradient(135deg,'+t[0]+','+t[1]+','+t[2]+')';d.onclick=()=>{stopRainbow();applyT(...t);if(host==='pal')toast('🎨 '+(name||''))};return d}
 NT.forEach(n=>$('themes').appendChild(sw(n.slice(1),n[0])));
 // لوحة ألوان عايمة
 const pb=document.createElement('button');pb.id='palBtn';pb.textContent='🎨';pb.title='Colors';
 const pp=document.createElement('div');pp.id='pal';pp.innerHTML='<b>🎨 اختار مزاجك</b><div class="g"></div><button class="format-btn" id="pR">🎲 عشوائي</button> <button class="format-btn" id="pW">🌈 قوس قزح</button>';
 document.body.append(pb,pp);const g=pp.querySelector('.g');
 TH.forEach((t,i)=>g.appendChild(sw(t,i>=18?NT[i-18][0]:'',  'pal')));
 pb.onclick=()=>pp.classList.toggle('on');$('pR').onclick=randomTheme;$('pW').onclick=toggleRainbow;
 addEventListener('click',e=>{if(!pp.contains(e.target)&&e.target!==pb)pp.classList.remove('on')});
 // سبوت لايت على الكروت
 document.addEventListener('pointermove',e=>{const c=e.target.closest&&e.target.closest('.card');if(!c)return;const r=c.getBoundingClientRect();c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px')});
})();

// ========== v9: سرعة + ميزات ==========
drawMatrix=function(){};
(function(){
 if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js').catch(()=>{});
 window.dp=null;addEventListener('beforeinstallprompt',e=>{e.preventDefault();window.dp=e;$('instBtn').style.display=''});
 $('instBtn').onclick=ev=>{ev.preventDefault();if(dp){dp.prompt();dp=null}else toast('اعمل التقييم من ⋮ ثم "إضافة للشاشة الرئيسية"')};
 // وضع الأداء
 function setLite(v){document.body.classList.toggle('lite',v);try{localStorage.setItem('mx_lite',v?'1':'0')}catch(e){}}
 let sv=null;try{sv=localStorage.getItem('mx_lite')}catch(e){}
 if(sv==='1'||(sv===null&&((navigator.hardwareConcurrency||8)<=4||(navigator.deviceMemory||8)<=4)))document.body.classList.add('lite');
 const pp=$('pal');if(pp){pp.insertAdjacentHTML('beforeend',' <button class="format-btn" id="pL">⚡ وضع الأداء</button>');$('pL').onclick=()=>{setLite(!document.body.classList.contains('lite'));toast(document.body.classList.contains('lite')?'⚡ ON':'✨ OFF')}}
 // مؤقت بين التحديثات
 let cd=0;const _hs=handleSubmit;handleSubmit=function(){const w=Math.ceil((cd-Date.now())/1000);if(w>0)return toast('استنى ثواني قبل التحديث الجاي ⏳ ('+w+')');return _hs.apply(this,arguments)};
 const _sr4=showResult;showResult=function(t,a,b){if(t==='success')cd=Date.now()+20000;_sr4(t,a,b)};
 const A=document.querySelector('.colA'),B=document.querySelector('.colB');if(!A||!B)return;
 const mk=(id,t,h)=>{const c=document.createElement('div');c.className='card rv in';c.id=id;c.innerHTML='<h3>'+t+'</h3>'+h;return c};
 const authCard=A.lastElementChild;
 // --- مولد الخطوط ---
 const FM=[['Bold',0x1D400,0x1D41A],['Italic',0x1D434,0x1D44E],['Bold Italic',0x1D468,0x1D482],['Script',0x1D4D0,0x1D4EA],['Fraktur',0x1D56C,0x1D586],['Sans Bold',0x1D5D4,0x1D5EE],['Sans Italic',0x1D608,0x1D622],['Mono',0x1D670,0x1D68A],['Circled',0x24B6,0x24D0],['Wide',0xFF21,0xFF41],['Small Caps',0,0]];
 const SC='ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ';
 function conv(t,f){return Array.from(t).map(ch=>{const c=ch.charCodeAt(0);if(f[0]==='Small Caps'){if(c>=97&&c<=122)return SC[c-97];if(c>=65&&c<=90)return SC[c-65];return ch}
  if(c>=65&&c<=90)return String.fromCodePoint(f[1]+c-65);if(c>=97&&c<=122){if(f[0]==='Italic'&&ch==='h')return 'ℎ';return String.fromCodePoint(f[2]+c-97)}return ch}).join('')}
 const fc=mk('secFont','🔤 مولد الخطوط والزخرفة','<input id="fgIn" placeholder="اكتب اسمك بالإنجليزي" style="direction:ltr" maxlength="40"><div id="fgOut"></div>');
 // --- تدرج ---
 const gc=mk('secGrad','🌈 تدرج لوني للنص','<div class="row"><label>🎨 من</label><input type="color" id="gA" value="#00f0ff"></div><div class="row"><label>إلى</label><input type="color" id="gB" value="#ff2bd6"></div><div class="row"><label>كل كام حرف</label><select id="gS" style="width:90px"><option>1</option><option>2</option><option>3</option></select></div><button class="format-btn" id="gGo" style="margin-top:10px">🌈 طبّق التدرج على البايو</button>');
 // --- رموز ---
 const sc=mk('secSym','✨ مكتبة الرموز','<div class="swg" id="symG"></div>');
 // --- صورة ---
 const ic=mk('secImg','🖼️ البايو كصورة','<button class="format-btn" id="iGo">🖼️ إنشاء الصورة</button><button class="format-btn" id="iDl">⬇️ تحميل</button><button class="format-btn" id="iSh">📤 مشاركة الصورة</button><canvas id="imgC" width="1080" height="540"></canvas>');
 [fc,gc,sc,ic].forEach(c=>A.insertBefore(c,authCard));
 const mc=mk('secMus','🎵 مشغل الموسيقى','<div class="row"><label>🔊 الصوت</label><input type="range" id="vol" min="0" max="100" value="75" style="flex:2"></div><button class="format-btn" id="mPl">⏯ تشغيل / إيقاف</button><label class="format-btn" style="display:inline-block;cursor:pointer">🎧 أغنية من جهازك<input type="file" id="mF" accept="audio/*" style="display:none"></label><button class="format-btn" id="mDf">↺ الأغنية الأساسية</button>');
 B.appendChild(mc);
 // wiring: fonts
 const fo=$('fgOut');function rf(){const t=$('fgIn').value;fo.innerHTML='';if(!t.trim())return;FM.forEach(f=>{const r=document.createElement('div');r.className='item';const o=conv(t,f);const d=document.createElement('div');d.style.fontSize='1.15rem';d.textContent=o;const u=document.createElement('button');u.textContent='استخدام';u.onclick=()=>{ins(o);toast('✅ تم الاستخدام')};const c=document.createElement('button');c.textContent='نسخ';c.onclick=()=>copyBio(o);r.append(d,u,c);fo.appendChild(r)})}
 $('fgIn').addEventListener('input',rf);
 // symbols
 '꧁ ꧂ ★ ☆ ✦ ✧ ❖ ♛ ♕ ⚔ ☠ ⚡ ☯ ✪ ◈ ∞ ☽ ☾ ♡ ❤ ✿ ❀ ➳ ༒ 𖤐 ⌬ ✈ ☬ ♠ ♣ ♥ ♦ ➤ ✔ ✘ ⚜ ❝ ❞ ツ シ ꨄ ₪ ♬ ☄ ✺ ❂ ⚘ ☀ ☁ ☂ ☃ ⚓ ✂ ✎ ☎ ✉'.split(' ').forEach(y=>{const b=document.createElement('button');b.className='format-btn';b.textContent=y;b.onclick=()=>ins(y);$('symG').appendChild(b)});
 // gradient
 const h2=c=>[1,3,5].map(i=>parseInt(c.slice(i,i+2),16));
 function toks(t){const o=[];let i=0;while(i<t.length){if(t[i]==='['&&t.length>=i+3&&t[i+2]===']'&&'bicus'.includes(t[i+1])){o.push({tag:t.slice(i,i+3)});i+=3}else if(t[i]==='['&&t.length>=i+8&&t[i+7]===']'&&/^[0-9A-Fa-f]{6}$/.test(t.slice(i+1,i+7))){i+=8}else{const cp=String.fromCodePoint(t.codePointAt(i));o.push({ch:cp});i+=cp.length}}return o}
 $('gGo').onclick=()=>{const T=toks($('bio').value);const n=T.filter(x=>x.ch&&x.ch!==' ').length;if(!n)return toast('اكتب البايو الأول');const a=h2($('gA').value),b=h2($('gB').value),st=+$('gS').value;let j=0,out='';
  T.forEach(x=>{if(x.tag){out+=x.tag;return}if(x.ch===' '){out+=' ';return}const k=n>1?j/(n-1):0;if(j%st===0)out+='['+a.map((v,i)=>Math.round(v+(b[i]-v)*k).toString(16).padStart(2,'0')).join('').toUpperCase()+']';out+=x.ch;j++});
  if(out.length>250)return toast('التدرج طويل — قصّر النص أو زوّد كل كام حرف');$('bio').value=out;$('bio').dispatchEvent(new Event('input'));toast('✅ تم تطبيق التدرج')};
 // image
 function bioImg(){const raw=$('bio').value;if(!raw)return toast('اكتب البايو الأول'),false;const W=1080,H=540,c=$('imgC'),x=c.getContext('2d'),cs=getComputedStyle(document.documentElement);const V=k=>cs.getPropertyValue(k).trim();
  const g=x.createLinearGradient(0,0,W,H);g.addColorStop(0,V('--b1')||'#05051a');g.addColorStop(1,V('--b2')||'#1b0a40');x.fillStyle=g;x.fillRect(0,0,W,H);
  [[160,120,V('--a')],[920,420,V('--a2')]].forEach(p=>{const r=x.createRadialGradient(p[0],p[1],0,p[0],p[1],320);r.addColorStop(0,p[2]+'55');r.addColorStop(1,'transparent');x.fillStyle=r;x.fillRect(0,0,W,H)});
  x.strokeStyle=V('--a');x.lineWidth=4;x.strokeRect(24,24,W-48,H-48);
  const runs=[];let col='#ffffff';
  // الألوان: toks بيشيل تاجات الألوان، فبنعيد قراءتها يدوي
  runs.length=0;let i=0,cur='',st={c:col,b:0,i:0};const flush=()=>{if(cur){runs.push({t:cur,c:st.c,b:st.b,i:st.i});cur=''}};
  while(i<raw.length){const ch=raw[i];if(ch==='['&&raw[i+7]===']'&&/^[0-9A-Fa-f]{6}$/.test(raw.slice(i+1,i+7))){flush();st={c:'#'+raw.slice(i+1,i+7),b:st.b,i:st.i};i+=8;continue}
   if(ch==='['&&raw[i+2]===']'&&'bicus'.includes(raw[i+1])){flush();const k=raw[i+1];if(k==='b')st={c:st.c,b:st.b?0:1,i:st.i};else if(k==='i'||k==='c')st={c:st.c,b:st.b,i:st.i?0:1};i+=3;continue}
   const cp=String.fromCodePoint(raw.codePointAt(i));cur+=cp;i+=cp.length}flush();
  const rtl=/[؀-ۿ]/.test(raw);let size=70,lines;const maxW=W-160;
  for(;size>=26;size-=4){lines=[];let ln={w:0,t:[]};const font=(r)=>(r.i?'italic ':'')+(r.b?'bold ':'')+size+'px Cairo,Arial,sans-serif';
   const words=[];let w={t:[],w:0};runs.forEach(r=>{x.font=font(r);r.t.split(' ').forEach((p,k,arr)=>{if(p){const m=x.measureText(p).width;w.t.push({s:p,r:r,m:m,f:font(r)});w.w+=m}if(k<arr.length-1){if(w.t.length)words.push(w);w={t:[],w:0};words.push({sp:1})}})});if(w.t.length)words.push(w);
   x.font=size+'px Cairo,Arial';const spW=x.measureText(' ').width;
   words.forEach(wd=>{if(wd.sp){if(ln.t.length){ln.t.push({sp:1});ln.w+=spW}return}if(ln.w+wd.w>maxW&&ln.t.length){lines.push(ln);ln={w:0,t:[]}}wd.t.forEach(q=>ln.t.push(q));ln.w+=wd.w});if(ln.t.length)lines.push(ln);
   if(lines.length*size*1.45<=H-170)break}
  const lh=size*1.45,y0=(H-lines.length*lh)/2+size*.8;x.textBaseline='alphabetic';
  lines.forEach((l,ri)=>{const items=rtl?l.t.slice().reverse():l.t;let px=rtl?(W+l.w)/2:(W-l.w)/2;items.forEach(q=>{if(q.sp){px+=rtl?-spW:spW;return}x.font=q.f;x.fillStyle=q.r.c;x.shadowColor=q.r.c;x.shadowBlur=14;if(rtl){px-=q.m;x.fillText(q.s,px,y0+ri*lh)}else{x.fillText(q.s,px,y0+ri*lh);px+=q.m}});x.shadowBlur=0});
  x.font='bold 22px Cairo,Arial';x.fillStyle=V('--a');x.textAlign='center';x.fillText('MODYXBIO',W/2,H-42);x.textAlign='start';c.style.display='block';return true}
 $('iGo').onclick=bioImg;
 $('iDl').onclick=()=>{if(!bioImg())return;$('imgC').toBlob(b=>{const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='MODYXBIO-bio.png';document.body.appendChild(a);a.click();a.remove()})};
 $('iSh').onclick=()=>{if(!bioImg())return;$('imgC').toBlob(b=>{const fl=new File([b],'MODYXBIO-bio.png',{type:'image/png'});if(navigator.canShare&&navigator.canShare({files:[fl]}))navigator.share({files:[fl],title:'MODYXBIO'}).catch(()=>{});else{const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='MODYXBIO-bio.png';a.click()}})};
 // music
 $('vol').oninput=e=>{bgm.volume=e.target.value/100};$('mPl').onclick=toggleMusic;$('mF').onchange=e=>{const f=e.target.files[0];if(!f)return;bgm.src=URL.createObjectURL(f);off=false;startMusic()};$('mDf').onclick=()=>{bgm.src='/music';off=false;startMusic()};
 // export/import
 $('savedList').insertAdjacentHTML('afterend','<div style="margin-top:10px"><button class="format-btn" id="xE">⬇️ تصدير</button><label class="format-btn" style="display:inline-block;cursor:pointer">⬆️ استيراد<input type="file" id="xI" accept=".json" style="display:none"></label></div>');
 $('xE').onclick=()=>{const b=new Blob([JSON.stringify(LS.get('mx_saved',[]))],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='modyxbio-saved.json';a.click()};
 $('xI').onchange=e=>{const f=e.target.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{try{const n=JSON.parse(r.result),l=LS.get('mx_saved',[]);n.forEach(x=>{if(x&&typeof x.bio==='string'&&!l.some(y=>y.bio===x.bio))l.push({t:x.t||Date.now(),bio:x.bio.slice(0,250)})});LS.set('mx_saved',l.slice(0,60));renderSaved();toast('✅ تم الاستيراد')}catch(err){toast('⚠️ حصلت مشكلة')}};r.readAsText(f)};
 // جولة
 const TS=[['secEd','✏️ اكتب بايوك هنا وزوّقه بالألوان والقوالب والخطوط'],['secCol','🎨 غيّر ألوان الموقع كلها من هنا أو من زرار 🎨 العايم'],['secGal','🌍 شوف بايوهات الناس واستخدمها واعمل لايك ❤️'],['secCt','📞 أي استفسار؟ كلّم المطور']];
 const tr=document.createElement('div');tr.id='tour';tr.innerHTML='<p id="tP"></p><small id="tN"></small> <button class="format-btn" id="tX">التالي ▶</button><button class="format-btn" id="tS" style="background:#444;color:#fff">تخطي</button>';document.body.appendChild(tr);
 let ti=0;window.startTour=function(){ti=0;stepTour()};
 function stepTour(){if(ti>=TS.length){tr.classList.remove('on');try{localStorage.setItem('mx_tour','1')}catch(e){}return}const t=TS[ti];$('tP').textContent=t[1];$('tN').textContent=(ti+1)+' / '+TS.length;tr.classList.add('on');const e=$(t[0]);if(e)e.scrollIntoView({behavior:'smooth',block:'start'})}
 $('tX').onclick=()=>{ti++;stepTour()};$('tS').onclick=()=>{ti=99;stepTour()};
 let seen=null;try{seen=localStorage.getItem('mx_tour')}catch(e){}
 if(!seen){const iv=setInterval(()=>{if(!$('submitBtn').disabled){clearInterval(iv);setTimeout(startTour,1200)}},700)}
})();

// ========== v10: إعدادات من لوحة المطور + تطبيق ==========
var RP=[],CT={tg:'MODYXBOT1',tt:'king_burd',wa:'201204564384'},CFG={},DEF={};
function fx(t){RP.forEach(p=>{t=t.split(p[0]).join(p[1])});return t}
function T0(el){const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n,o='';while(n=w.nextNode())o+=(orig.get(n)||n.nodeValue);return o.trim()}
function snap(){const q=(r,a)=>[...document.querySelectorAll(r)].map(a);
 DEF={feats:q('#secFeat .feat',e=>[T0(e.querySelector('i')),T0(e.querySelector('b')),T0(e.querySelector('p'))]),steps:q('#secHow .feat',e=>[T0(e.querySelector('b')),T0(e.querySelector('p'))]),faqs:q('#secFaq details',e=>[T0(e.querySelector('summary')),T0(e.querySelector('p'))]),tpls:TP.map(x=>[x[0],x[1]])}}
snap();
function rep(a,b){document.querySelectorAll('a[href]').forEach(x=>{const h=x.getAttribute('href');if(h.includes(a))x.setAttribute('href',h.split(a).join(b))});
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,{acceptNode:n=>['SCRIPT','STYLE','TEXTAREA'].includes(n.parentNode.nodeName)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});const a2=[];let n;while(n=w.nextNode())if(n.nodeValue.includes(a))a2.push(n);a2.forEach(n=>{n.nodeValue=n.nodeValue.split(a).join(b)})}
const SEC={tpl:'secTpl',fmt:'secFmt',bc:'secBC',col:'secCol',gal:'secGal',stats:'secStats',rate:'secRate',saved:'secSaved',hist:'secHist',gb:'secGb',share:'secShare',msg:'secMsg',font:'secFont',grad:'secGrad',sym:'secSym',img:'secImg',mus:'secMus',feat:'secFeat',how:'secHow',faq:'secFaq',app:'secApp'};
const SECL={tpl:'القوالب',fmt:'التنسيق',bc:'ألوان البايو',col:'ألوان الموقع',gal:'المعرض',stats:'الإحصائيات',rate:'التقييم',saved:'المحفوظات',hist:'السجل',gb:'دفتر الزوار',share:'المشاركة',msg:'رسالة المطور',font:'مولد الخطوط',grad:'التدرج',sym:'الرموز',img:'البايو كصورة',mus:'المشغل',feat:'المميزات',how:'طريقة الاستخدام',faq:'الأسئلة',app:'تحميل التطبيق'};
function applyCfg(){const c=CFG;RP.length=0;
 const cl=v=>String(v).replace('@','').trim();
 if(c.tg_user){CT.tg=cl(c.tg_user);RP.push(['MODYXBOT1',CT.tg])}
 if(c.tt_user){CT.tt=cl(c.tt_user);RP.push(['king_burd',CT.tt])}
 if(c.wa_num){const n=cl(c.wa_num).split(' ').join('');CT.wa=n;RP.push(['201204564384',n]);RP.push(['01204564384',n.indexOf('20')===0?'0'+n.slice(2):n])}
 if(c.dev_name)RP.push(['𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅',c.dev_name]);
 if(c.dev_fms)RP.push(['𝒁𝑨𝑨𝑻𝑨𝑹',c.dev_fms]);
 if(c.site_name)RP.push(['𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶',c.site_name]);
 RP.forEach(p=>rep(p[0],p[1]));if(c.site_name)document.title=document.title.split('MODYXBIO').join(c.site_name);
 if(c.hero_eyebrow)$('cEye').textContent=c.hero_eyebrow;if(c.hero_lead)$('cLead').textContent=c.hero_lead;
 if(c.app_text)$('appP').textContent=c.app_text;
 if(c.app_url){const a=$('appApk');a.href=c.app_url;a.style.display=''}
 if(c.apk){const a=$('appApk');a.href='/app.apk';a.removeAttribute('target');a.style.display=''}
 if(c.feats)document.querySelector('#secFeat .grid3').innerHTML=c.feats.map(f=>'<div class="feat"><i>'+esc(f[0])+'</i><b>'+esc(f[1])+'</b><p>'+esc(f[2])+'</p></div>').join('');
 if(c.steps)document.querySelector('#secHow .grid3').innerHTML=c.steps.map((f,i)=>'<div class="feat"><span class="num">'+(i+1)+'</span><b>'+esc(f[0])+'</b><p>'+esc(f[1])+'</p></div>').join('');
 if(c.faqs){$('secFaq').querySelectorAll('details').forEach(d=>d.remove());$('secFaq').insertAdjacentHTML('beforeend',c.faqs.map(f=>'<details><summary>'+esc(f[0])+'</summary><p>'+esc(f[1])+'</p></details>').join(''))}
 if(c.tpls){$('tpls').innerHTML='';c.tpls.forEach(p=>{const b=document.createElement('button');b.className='format-btn';b.textContent=p[0];b.onclick=()=>useBio(p[1]);$('tpls').appendChild(b)})}
 (c.hidden||[]).forEach(k=>{const e=$(SEC[k]);if(e)e.style.display='none'});
 if(c.ticker_on===false){$('ticker').style.display='none';document.documentElement.style.setProperty('--tk','0px')}
 if(c.ticker_speed)$('tk').style.animationDuration=c.ticker_speed+'s';
 if(c.mv)bgm.src='/music?v='+c.mv;
 if(c.default_theme&&c.ver){let sv=null;try{sv=localStorage.getItem('mx_cfgv')}catch(e){}if(String(sv)!==String(c.ver)){applyT(...c.default_theme);try{localStorage.setItem('mx_cfgv',c.ver)}catch(e){}}}
 buildTk();if(LANG==='en')trAll(document.body)}
fetch('/api/config').then(r=>r.json()).then(c=>{CFG=c||{};applyCfg()}).catch(()=>{});
// تثبيت التطبيق
function installApp(e){if(e)e.preventDefault();if(window.dp){window.dp.prompt();window.dp=null;return}
 const ios=/iphone|ipad|ipod/i.test(navigator.userAgent);$('helpT').textContent=ios?'📲 على iPhone: اضغط زرار المشاركة ⬆️ في Safari ثم "إضافة إلى الشاشة الرئيسية"':'📲 على أندرويد: اضغط ⋮ في المتصفح ثم "تثبيت التطبيق" أو "إضافة إلى الشاشة الرئيسية"';$('help').classList.add('on');if(LANG==='en')trAll($('help'))}
$('appInst').onclick=installApp;$('instBtn').onclick=installApp;
if((matchMedia('(display-mode: standalone)').matches)||navigator.standalone){$('appInst').style.display='none';$('instBtn').style.display='none';$('appHint').textContent='✅ التطبيق مثبّت عندك'}
// ===== لوحة المطور: إعدادات كل حاجة =====
function sp(l,n){const p=[];let r=l;for(let i=0;i<n-1;i++){const k=r.indexOf('|');if(k<0)break;p.push(r.slice(0,k).trim());r=r.slice(k+1)}p.push(r.trim());return p}
function F(id,lb,val,ph,ta){return '<label>'+lb+(ta?'<textarea id="'+id+'" placeholder="'+esc(ph||'')+'">'+esc(val||'')+'</textarea>':'<input id="'+id+'" value="'+esc(val||'')+'" placeholder="'+esc(ph||'')+'">')+'</label>'}
async function admCfgRender(){let d;try{d=await api('/api/admin/summary')}catch(e){return}if(!d||d.error)return;const c=d.cfg||{},th=c.default_theme||['#05051a','#1b0a40','#00f0ff','#ff2bd6'],hid=c.hidden||[];
 const L=(a,df)=>(a&&a.length?a:df||[]).map(r=>r.join(' | ')).join(NL);
 $('admCfg').innerHTML='<h3>⚙️ إعدادات الموقع</h3><h4>🏷️ الهوية والنصوص</h4>'
 +F('cf_site','اسم الموقع',c.site_name,'𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶')+F('cf_eye','الشارة فوق العنوان',c.hero_eyebrow,'🇪🇬 الشرق الأوسط • ME')+F('cf_lead','الفقرة التعريفية',c.hero_lead,'',1)
 +F('cf_dev','اسم المطور (Dev)',c.dev_name,'𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅')+F('cf_fms','اسم الشهرة (FMS)',c.dev_fms,'𝒁𝑨𝑨𝑻𝑨𝑹')
 +'<h4>📞 التواصل</h4>'+F('cf_tg','يوزر تليجرام (من غير @)',c.tg_user,'MODYXBOT1')+F('cf_tt','يوزر تيك توك (من غير @)',c.tt_user,'king_burd')+F('cf_wa','رقم واتساب بالصيغة الدولية',c.wa_num,'201204564384')
 +'<h4>📲 التطبيق</h4>'+F('cf_app','رابط تحميل APK أو متجر (اختياري)',c.app_url,'https://')+F('cf_apt','نص قسم التطبيق',c.app_text,'')
 +'<h4>🎨 الشكل والشريط</h4><div class="row"><label>خلفية 1</label><input type="color" id="cf_t1" value="'+th[0]+'"><label>خلفية 2</label><input type="color" id="cf_t2" value="'+th[1]+'"></div><div class="row"><label>أساسي</label><input type="color" id="cf_t3" value="'+th[2]+'"><label>ثانوي</label><input type="color" id="cf_t4" value="'+th[3]+'"></div>'
 +'<label class="chk"><input type="checkbox" id="cf_thon"> فرض الثيم ده على كل الزوار (مرة واحدة)</label><label class="chk"><input type="checkbox" id="cf_ton" '+(c.ticker_on===false?'':'checked')+'> إظهار شريط الإعلانات</label>'
 +'<label>سرعة الشريط (ثواني للدورة: أقل = أسرع)<input type="range" id="cf_tsp" min="10" max="120" value="'+(c.ticker_speed||45)+'"></label>'
 +'<h4>👁️ إخفاء أقسام</h4><div>'+Object.keys(SEC).map(k=>'<label class="chk"><input type="checkbox" class="cf_h" value="'+k+'" '+(hid.includes(k)?'checked':'')+'> '+SECL[k]+'</label>').join('')+'</div>'
 +'<h4>🧩 المحتوى (سطر لكل عنصر، الفصل بـ |)</h4>'+F('cf_fe','المميزات: أيقونة | عنوان | نص',L(c.feats,DEF.feats),'',1)+F('cf_st','الخطوات: عنوان | نص',L(c.steps,DEF.steps),'',1)+F('cf_fq','الأسئلة: سؤال | إجابة',L(c.faqs,DEF.faqs),'',1)+F('cf_tp','القوالب: اسم | البايو',L(c.tpls,DEF.tpls),'',1)
 +'<button class="format-btn" style="width:100%;margin-top:12px" onclick="admSaveCfg()">💾 حفظ كل الإعدادات</button>'
 +'<h4>🎵 موسيقى الموقع</h4><label class="format-btn" style="display:inline-block;cursor:pointer">⬆️ ارفع أغنية mp3 (لحد 25MB)<input type="file" accept="audio/*" style="display:none" onchange="admMusic(this)"></label><button class="format-btn" onclick="admMusicReset()">↺ الأغنية الأصلية</button>'
 +'<h4>🔑 تغيير كلمة السر</h4><input id="cf_pw" type="password" placeholder="كلمة السر الجديدة (8 حروف+)"><button class="format-btn" onclick="admPw()" style="margin-top:8px">تغيير</button>'}
function admSaveCfg(){const g=id=>$(id).value.trim();const o={site_name:g('cf_site'),hero_eyebrow:g('cf_eye'),hero_lead:g('cf_lead'),dev_name:g('cf_dev'),dev_fms:g('cf_fms'),tg_user:g('cf_tg'),tt_user:g('cf_tt'),wa_num:g('cf_wa'),app_url:g('cf_app'),app_text:g('cf_apt'),ticker_on:$('cf_ton').checked,ticker_speed:+$('cf_tsp').value,hidden:[...document.querySelectorAll('.cf_h:checked')].map(x=>x.value)};
 if($('cf_thon').checked)o.default_theme=['cf_t1','cf_t2','cf_t3','cf_t4'].map(i=>$(i).value);
 const P=(id,n)=>g(id).split(NL).map(l=>sp(l,n)).filter(a=>a.length===n&&a[0]);
 [['feats','cf_fe',3],['steps','cf_st',2],['faqs','cf_fq',2],['tpls','cf_tp',2]].forEach(x=>{const r=P(x[1],x[2]);if(r.length)o[x[0]]=r});
 api('/api/admin/config',o).then(d=>{if(d.ok){toast('✅ تم حفظ الإعدادات');setTimeout(()=>location.reload(),900)}else toast('⚠️ حصلت مشكلة')}).catch(()=>toast('⚠️ حصلت مشكلة'))}
async function admMusic(i){const f=i.files[0];if(!f)return;const fd=new FormData();fd.append('file',f);toast('⏳ جاري الرفع...');try{const r=await fetch('/api/admin/music',{method:'POST',headers:{'X-Token':TOK},body:fd});const d=await r.json();toast(d.ok?'✅ تم تغيير الأغنية':'⚠️ '+(d.error||''))}catch(e){toast('⚠️ حصلت مشكلة')}}
async function admMusicReset(){try{await fetch('/api/admin/music',{method:'DELETE',headers:{'X-Token':TOK}});toast('✅ رجعت الأغنية الأصلية')}catch(e){toast('⚠️ حصلت مشكلة')}}
async function admPw(){const d=await api('/api/admin/password',{pass:$('cf_pw').value});toast(d.ok?'✅ تم تغيير كلمة السر':'⚠️ '+(d.error||''));if(d.ok)$('cf_pw').value=''}
const _ar2=admRender;admRender=async function(){await _ar2();if(TOK)admCfgRender()};
</script>
<script>
// ===== بوابة الصلاة على النبي ﷺ =====
(function(){
 const g=document.getElementById('sal');if(!g)return;
 const cnt=document.getElementById('salCnt'),thx=document.getElementById('salThx');
 const TXT='اللهم صل وسلم وبارك على سيدنا محمد وعلى آله وصحبه أجمعين';
 let hasAudio=0,busy=false;
 // الموسيقى تستنى لحد ما الصلاة تخلص
 try{bgm.pause();off=true;icon()}catch(e){}
 function showCnt(n){if(cnt&&n>0)cnt.innerHTML='صلّى على النبي ﷺ هنا <b>'+Number(n).toLocaleString('ar-EG')+'</b> مرة'}
 fetch('/api/salawat').then(r=>r.json()).then(d=>showCnt(d.count)).catch(()=>{});
 fetch('/api/config').then(r=>r.json()).then(c=>{hasAudio=(c&&c.sal)||0}).catch(()=>{});
 function tts(done){
  try{
   const S=window.speechSynthesis;
   if(!S||!window.SpeechSynthesisUtterance){setTimeout(done,4500);return}
   S.cancel();
   const u=new SpeechSynthesisUtterance(TXT);u.lang='ar-SA';u.rate=.8;u.pitch=1;u.volume=1;
   const v=S.getVoices().find(x=>/^ar/i.test(x.lang));if(v){u.voice=v;u.lang=v.lang}
   let f=false;const d=()=>{if(!f){f=true;done()}};
   u.onend=d;u.onerror=d;S.speak(u);
  }catch(e){setTimeout(done,4500)}
 }
 function finish(){
  g.classList.add('done');thx.textContent='جزاك الله خيرًا';
  try{sessionStorage.setItem('mx_sal','1')}catch(e){}
  fetch('/api/salawat',{method:'POST'}).then(r=>r.json()).then(d=>showCnt(d.count)).catch(()=>{});
  setTimeout(()=>{g.classList.add('off');try{off=false}catch(e){}setTimeout(()=>g.remove(),1000)},1800);
 }
 function go(){
  if(busy)return;busy=true;g.classList.add('go');
  const t0=Date.now();let ended=false;
  const end=()=>{if(ended)return;ended=true;setTimeout(finish,Math.max(0,4500-(Date.now()-t0)))};
  setTimeout(end,14000);
  if(hasAudio){
   const a=new Audio('/salawat?v='+hasAudio);a.onended=end;a.onerror=()=>tts(end);
   a.play().catch(()=>tts(end));
  }else tts(end);
 }
 document.getElementById('salBtn').onclick=go;
 try{document.getElementById('salBtn').focus({preventScroll:true})}catch(e){}
})();

</script>
</body>
</html>
"""

API_BASE_URL = "https://drogon-bio-api.vercel.app/bio"

STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.json')
_lock = threading.Lock()

def _load_stats():
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {"visits": 0, "updates": 0, "failed": 0}

def _bump(key, n=1):
    with _lock:
        d = _load_stats()
        d[key] = d.get(key, 0) + n
        try:
            with open(STATS_FILE, 'w', encoding='utf-8') as fh:
                json.dump(d, fh)
        except Exception:
            pass
        return d

@app.route('/api/visit', methods=['POST'])
def api_visit():
    _daily_bump()
    return jsonify(_bump('visits'))

@app.route('/api/stats')
def api_stats():
    return jsonify(_load_stats())

# ===== كلمة سر لوحة المطور: غيّرها من هنا أو بمتغير بيئة ADMIN_PASS =====
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'MODYXBOTBIO')
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
_hits = {}

def _ip():
    return (request.headers.get('X-Forwarded-For') or request.remote_addr or '').split(',')[0].strip()

def _limit(key, seconds):
    now = time.time()
    k = key + _ip()
    if now - _hits.get(k, 0) < seconds:
        return True
    _hits[k] = now
    return False

def _jload(name, default):
    try:
        with open(os.path.join(DATA_DIR, name), 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return default

def _jsave(name, data):
    with _lock:
        try:
            with open(os.path.join(DATA_DIR, name), 'w', encoding='utf-8') as fh:
                json.dump(data, fh, ensure_ascii=False)
        except Exception:
            pass

_SECRET = None


def _secret():
    global _SECRET
    if _SECRET:
        return _SECRET
    v = os.environ.get('SECRET_KEY', '')
    if not v:
        p = os.path.join(DATA_DIR, 'secret.key')
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                v = fh.read().strip()
        except Exception:
            v = ''
        if not v:
            v = secrets.token_hex(32)
            try:
                with open(p, 'w', encoding='utf-8') as fh:
                    fh.write(v)
            except Exception:
                v = hashlib.sha256(('mx' + ADMIN_PASS).encode()).hexdigest()
    _SECRET = v
    return v


def _pw_fp():
    a = _jload('admin.json', None)
    return a.get('hash', '') if a else hashlib.sha256(ADMIN_PASS.encode()).hexdigest()


def _sig(msg):
    return hmac.new((_secret() + _pw_fp()).encode(), msg.encode(), hashlib.sha256).hexdigest()


def _make_token():
    # توكن موقّع بصلاحية 12 ساعة (بيشتغل حتى لو السيرفر فيه أكتر من worker)
    msg = '%d.%s' % (int(time.time()) + 43200, secrets.token_hex(6))
    return msg + '.' + _sig(msg)


def _is_admin():
    t = request.headers.get('X-Token', '')
    try:
        exp, rnd, sig = t.split('.')
        return int(exp) > time.time() and hmac.compare_digest(sig, _sig(exp + '.' + rnd))
    except Exception:
        return False


def _daily_bump():
    day = time.strftime('%Y-%m-%d')
    with _glock:
        d = _jload('daily.json', {})
        d[day] = d.get(day, 0) + 1
        keys = sorted(d)[-60:]
        _jsave('daily.json', {k: d[k] for k in keys})

@app.route('/api/rate', methods=['POST'])
def api_rate():
    d = request.get_json(silent=True) or {}
    try:
        n = int(d.get('stars', 0))
    except Exception:
        n = 0
    if n < 1 or n > 5:
        return jsonify({"error": "تقييم غير صالح"}), 400
    if _limit('rate', 3600):
        return jsonify({"error": "قيّمت قبل كده ⭐"}), 429
    _bump('rate_sum', n)
    return jsonify(_bump('rate_n'))

@app.route('/api/guest', methods=['GET', 'POST'])
def api_guest():
    g = _jload('guestbook.json', [])
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        name = str(d.get('name', '')).strip()[:30] or 'زائر'
        text = str(d.get('text', '')).strip()[:200]
        if len(text) < 2:
            return jsonify({"error": "اكتب تعليق الأول"}), 400
        if _limit('gb', 30):
            return jsonify({"error": "استنى شوية قبل التعليق الجاي ⏳"}), 429
        ms = int(time.time() * 1000)
        g.append({"id": ms, "name": name, "text": text, "t": ms})
        g = g[-200:]
        _jsave('guestbook.json', g)
    return jsonify({"list": list(reversed(g))[:30]})

_glock = threading.Lock()

def _publish(bio):
    # بيتحفظ نص البايو بس - من غير توكن ولا UID ولا اسم
    bio = (bio or '').strip()[:250]
    if len(bio) < 3:
        return
    with _glock:
        g = _jload('gallery.json', [])
        if any(x.get('bio') == bio for x in g):
            return
        ms = int(time.time() * 1000)
        g.append({"id": ms, "bio": bio, "t": ms, "likes": 0, "uses": 0, "lk": []})
        _jsave('gallery.json', g[-500:])

def _pub(x):
    return {k: v for k, v in x.items() if k != 'lk'}

@app.route('/api/gallery')
def api_gallery():
    g = _jload('gallery.json', [])
    if request.args.get('sort') == 'top':
        g.sort(key=lambda x: (x.get('likes', 0), x.get('t', 0)), reverse=True)
    else:
        g = list(reversed(g))
    return jsonify({"list": [_pub(x) for x in g[:30]]})

@app.route('/api/gallery/like', methods=['POST'])
def gallery_like():
    d = request.get_json(silent=True) or {}
    h = hashlib.sha256((_ip() + 'mx').encode()).hexdigest()[:12]
    with _glock:
        g = _jload('gallery.json', [])
        for x in g:
            if x.get('id') == d.get('id'):
                lk = x.setdefault('lk', [])
                if h in lk:
                    return jsonify({"likes": x.get('likes', 0), "already": True})
                lk.append(h)
                x['likes'] = x.get('likes', 0) + 1
                _jsave('gallery.json', g)
                return jsonify({"likes": x['likes']})
    return jsonify({"error": "not found"}), 404

@app.route('/api/gallery/use', methods=['POST'])
def gallery_use():
    d = request.get_json(silent=True) or {}
    with _glock:
        g = _jload('gallery.json', [])
        for x in g:
            if x.get('id') == d.get('id'):
                x['uses'] = x.get('uses', 0) + 1
                _jsave('gallery.json', g)
                return jsonify({"uses": x['uses']})
    return jsonify({"error": "not found"}), 404

@app.route('/api/admin/gallery/delete', methods=['POST'])
def admin_gallery_delete():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    d = request.get_json(silent=True) or {}
    with _glock:
        g = [x for x in _jload('gallery.json', []) if x.get('id') != d.get('id')]
        _jsave('gallery.json', g)
    return jsonify({"ok": True})

@app.route('/api/ads')
def api_ads():
    return jsonify(_jload('ads.json', None))

_fails = {}


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    ip = _ip()
    now = time.time()
    n, until = _fails.get(ip, (0, 0))
    if until > now:
        return jsonify({"error": "🔒 محاولات غلط كتير. استنى %d دقيقة وحاول تاني" % (int((until - now) // 60) + 1)}), 429
    if _limit('login', 1):
        return jsonify({"error": "استنى ثانية وحاول تاني"}), 429
    d = request.get_json(silent=True) or {}
    if _pass_ok(str(d.get('pass', ''))):
        _fails.pop(ip, None)
        return jsonify({"token": _make_token()})
    n += 1
    if n >= 5:
        _fails[ip] = (0, now + 600)
        return jsonify({"error": "🔒 محاولات غلط كتير. الدخول اتقفل 10 دقايق"}), 429
    _fails[ip] = (n, 0)
    return jsonify({"error": "❌ كلمة السر غلط (باقي %d محاولات)" % (5 - n)}), 403

def _fsize(name):
    try:
        return os.path.getsize(os.path.join(DATA_DIR, name))
    except Exception:
        return 0


@app.route('/api/admin/summary')
def admin_summary():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    g = _jload('guestbook.json', [])
    gal = _jload('gallery.json', [])
    daily = _jload('daily.json', {})
    days = []
    for k in range(13, -1, -1):
        d = time.strftime('%Y-%m-%d', time.localtime(time.time() - k * 86400))
        days.append({"d": d, "n": daily.get(d, 0)})
    return jsonify({
        "stats": _load_stats(),
        "guest": list(reversed(g))[:50],
        "ads": _jload('ads.json', None),
        "cfg": _jload('config.json', {}),
        "gallery": [_pub(x) for x in reversed(gal)][:50],
        "counts": {"guest": len(g), "gallery": len(gal)},
        "daily": days,
        "files": {"music": _fsize('music_custom.mp3'), "salawat": _fsize('salawat_custom.mp3'),
                  "apk": _fsize('app_custom.apk'), "logo": _fsize('logo_custom.png')},
    })

@app.route('/api/admin/ads', methods=['POST'])
def admin_ads():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    d = request.get_json(silent=True) or {}
    out = []
    for a in (d.get('ads') or [])[:20]:
        try:
            t, u = str(a[0]).strip()[:120], str(a[1]).strip()[:300]
        except Exception:
            continue
        if t and (u.startswith('http') or u == '#'):
            out.append([t, u])
    _jsave('ads.json', out)
    return jsonify({"ok": True, "count": len(out)})

@app.route('/api/admin/guest/delete', methods=['POST'])
def admin_guest_delete():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    d = request.get_json(silent=True) or {}
    g = [x for x in _jload('guestbook.json', []) if x.get('id') != d.get('id')]
    _jsave('guestbook.json', g)
    return jsonify({"ok": True})

@app.route('/api/admin/reset', methods=['POST'])
def admin_reset():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    _jsave('stats.json', {"visits": 0, "updates": 0, "failed": 0, "salawat": _load_stats().get('salawat', 0)})
    _jsave('daily.json', {})
    return jsonify({"ok": True})

@app.after_request
def _gz(resp):
    try:
        if (resp.status_code == 200 and 'gzip' in request.headers.get('Accept-Encoding', '')
                and resp.mimetype in ('text/html', 'application/json', 'text/javascript', 'application/javascript')
                and not resp.direct_passthrough and len(resp.get_data()) > 1024):
            data = gzip.compress(resp.get_data(), 5)
            resp.set_data(data)
            resp.headers['Content-Encoding'] = 'gzip'
            resp.headers['Vary'] = 'Accept-Encoding'
            resp.headers['Content-Length'] = str(len(data))
    except Exception:
        pass
    return resp

# ===== PWA: تثبيت كتطبيق =====
ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" fill="#05051a"/><circle cx="256" cy="256" r="220" fill="none" stroke="#00f0ff" stroke-width="14"/><circle cx="256" cy="256" r="178" fill="none" stroke="#ff2bd6" stroke-width="9"/><text x="256" y="330" font-size="230" font-weight="900" text-anchor="middle" fill="#ffd700" font-family="Arial">M</text></svg>'

@app.route('/icon.svg')
def icon_svg():
    return app.response_class(ICON_SVG, mimetype='image/svg+xml')

_logo_cache = {}


def _logo_raw():
    custom = os.path.join(DATA_DIR, 'logo_custom.png')
    if os.path.exists(custom):
        try:
            with open(custom, 'rb') as fh:
                return fh.read(), os.path.getmtime(custom)
        except Exception:
            pass
    return base64.b64decode(LOGO_B64), 0


def _logo_img(size=None):
    raw, mt = _logo_raw()
    key = (size, mt)
    if key in _logo_cache:
        return _logo_cache[key]
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        w, h = im.size
        m = min(w, h)
        im = im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))
        if size:
            im = im.resize((size, size), getattr(Image, 'Resampling', Image).LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        out = (buf.getvalue(), 'image/png')
    except Exception:
        out = (raw, 'image/jpeg')
    if len(_logo_cache) > 10:
        _logo_cache.clear()
    _logo_cache[key] = out
    return out


def _logo_resp(size=None):
    data, mime = _logo_img(size)
    r = app.response_class(data, mimetype=mime)
    r.headers['Cache-Control'] = 'public, max-age=600'
    return r


@app.route('/logo.png')
def logo_png():
    return _logo_resp()


@app.route('/favicon.ico')
def favicon():
    return _logo_resp(64)


@app.route('/icon-<int:size>.png')
def icon_png(size):
    return _logo_resp(192 if size < 300 else 512)


@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "MODYXBIO", "short_name": "MODYXBIO", "lang": "ar", "dir": "rtl",
        "description": "محرر بايو فري فاير: سريع، آمن، ومجاني",
        "start_url": "/", "display": "standalone", "background_color": "#050506", "theme_color": "#050506",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"}],
        "shortcuts": [{"name": "المحرر", "url": "/#secEd"}, {"name": "المعرض", "url": "/#secGal"}]})


SW_JS = """const C='mx-v2';
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(clients.claim())});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);
if(e.request.method!=='GET'||u.origin!==location.origin||u.pathname==='/music'||u.pathname==='/salawat'||u.pathname==='/app.apk'||u.pathname==='/admin'||u.pathname==='/logo.png'||u.pathname.indexOf('/api/')===0)return;
e.respondWith(caches.open(C).then(c=>c.match(e.request).then(m=>{const f=fetch(e.request).then(r=>{if(r.ok)c.put(e.request,r.clone());return r}).catch(()=>m);return m||f})))});"""

@app.route('/sw.js')
def sw():
    r = app.response_class(SW_JS, mimetype='application/javascript')
    r.headers['Service-Worker-Allowed'] = '/'
    return r

app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024

def _pass_ok(p):
    a = _jload('admin.json', None)
    if a:
        return hmac.compare_digest(hashlib.sha256((a.get('salt', '') + p).encode()).hexdigest(), a.get('hash', ''))
    return hmac.compare_digest(p, ADMIN_PASS)

def _music_path():
    custom = os.path.join(DATA_DIR, 'music_custom.mp3')
    return custom if os.path.exists(custom) else os.path.join(DATA_DIR, 'music.mp3')

_CFG_STR = ['site_name', 'hero_eyebrow', 'hero_lead', 'dev_name', 'dev_fms', 'tg_user', 'tt_user', 'wa_num', 'app_url', 'app_text']

def _clean_cfg(d):
    out = {}
    for k in _CFG_STR:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            out[k] = v.strip()[:600]
    th = d.get('default_theme')
    if isinstance(th, list) and len(th) == 4 and all(isinstance(x, str) and re.match(r'^#[0-9a-fA-F]{6}$', x) for x in th):
        out['default_theme'] = th
    sp = d.get('ticker_speed')
    if isinstance(sp, (int, float)) and 10 <= sp <= 200:
        out['ticker_speed'] = sp
    out['ticker_on'] = bool(d.get('ticker_on', True))
    hid = d.get('hidden')
    out['hidden'] = [str(x)[:20] for x in hid][:40] if isinstance(hid, list) else []
    for key, n, mx in (('feats', 3, 12), ('steps', 2, 8), ('faqs', 2, 20), ('tpls', 2, 30)):
        v = d.get(key)
        rows = []
        if isinstance(v, list):
            for it in v[:mx]:
                if isinstance(it, list) and len(it) >= n and all(isinstance(x, str) for x in it[:n]):
                    row = [x.strip()[:400] for x in it[:n]]
                    if row[0]:
                        rows.append(row)
        if rows:
            out[key] = rows
    out['ver'] = int(time.time() * 1000)
    return out

@app.route('/api/config')
def api_config():
    c = _jload('config.json', {})
    custom = os.path.join(DATA_DIR, 'music_custom.mp3')
    if os.path.exists(custom):
        c['mv'] = int(os.path.getmtime(custom))
    sal = os.path.join(DATA_DIR, 'salawat_custom.mp3')
    if os.path.exists(sal):
        c['sal'] = int(os.path.getmtime(sal)) or 1
    apk = os.path.join(DATA_DIR, 'app_custom.apk')
    if os.path.exists(apk):
        c['apk'] = os.path.getsize(apk)
    return jsonify(c)

@app.route('/api/admin/config', methods=['POST'])
def admin_config():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    c = _clean_cfg(request.get_json(silent=True) or {})
    _jsave('config.json', c)
    return jsonify({"ok": True, "cfg": c})

@app.route('/api/admin/password', methods=['POST'])
def admin_password():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    p = str((request.get_json(silent=True) or {}).get('pass', ''))
    if len(p) < 8:
        return jsonify({"error": "كلمة السر لازم 8 حروف على الأقل"}), 400
    salt = secrets.token_hex(8)
    _jsave('admin.json', {"salt": salt, "hash": hashlib.sha256((salt + p).encode()).hexdigest()})
    return jsonify({"ok": True})

@app.route('/api/admin/music', methods=['POST', 'DELETE'])
def admin_music():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    custom = os.path.join(DATA_DIR, 'music_custom.mp3')
    if request.method == 'DELETE':
        try:
            os.remove(custom)
        except Exception:
            pass
        return jsonify({"ok": True})
    f = request.files.get('file')
    if not f or not (f.mimetype or '').startswith('audio'):
        return jsonify({"error": "ملف صوتي فقط (mp3)"}), 400
    f.save(custom)
    return jsonify({"ok": True})

@app.route('/music')
def music():
    return send_file(_music_path(), mimetype='audio/mpeg', conditional=True, max_age=86400)

@app.route('/')
def index():
    return HTML_TEMPLATE.replace('__ORIGIN__', request.url_root.rstrip('/'))

@app.route('/api/update', methods=['POST'])
def update_bio():
    if _limit('upd', 8):
        return jsonify({"status": "error", "message": "استنى ثواني قبل التحديث الجاي ⏳"}), 429
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Missing JSON body"}), 400

        method = data.get('method', 'jwt')
        bio = data.get('bio', '').strip()
        server = data.get('server', 'ME')
        token = data.get('token', '').strip()
        password = data.get('password', '').strip()

        if not bio:
            return jsonify({"status": "error", "message": "Bio is required"}), 400
        if not token:
            return jsonify({"status": "error", "message": "Token/UID is required"}), 400

        params = {"bio": bio}

        if method == 'uid':
            if not password:
                return jsonify({"status": "error", "message": "Password required for UID method"}), 400
            params['uid'] = token
            params['pass'] = password
        elif method == 'jwt':
            params['jwt'] = token
        elif method == 'eat':
            params['eat'] = token
        elif method == 'access':
            params['access'] = token
        else:
            return jsonify({"status": "error", "message": f"Unsupported method: {method}"}), 400

        # Server selection via region param (optional, but we include it)
        # The API doesn't explicitly document server param, but we pass it as region if needed
        params['region'] = server  # Some APIs use 'region'

        # Make the request to the external API
        response = requests.get(API_BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        api_data = response.json()

        # Extract relevant fields for frontend
        result = {
            "status": "success" if api_data.get('success') else "error",
            "message": api_data.get('status', 'Bio updated'),
            "uid": api_data.get('uid'),
            "name": api_data.get('name'),
            "region_used": api_data.get('region_used'),
            "login_method": api_data.get('login_method'),
            "server_response": api_data.get('server_response'),
            "generated_jwt": api_data.get('generated_jwt'),  # if returned
            "http_code": api_data.get('http_code'),
        }

        # If API returned success=false, treat as error
        if not api_data.get('success', False):
            result["status"] = "error"
            result["message"] = api_data.get('status', 'API returned failure')

        _bump('updates' if result['status'] == 'success' else 'failed')
        if result['status'] == 'success' and data.get('publish', True):
            _publish(bio)
        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"API request failed: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

# ================= v11: الصلاة على النبي / لوحة التحكم / الوسائط =================
@app.route('/api/salawat', methods=['GET', 'POST'])
def api_salawat():
    if request.method == 'POST' and not _limit('sal', 15):
        return jsonify({"count": _bump('salawat').get('salawat', 0)})
    return jsonify({"count": _load_stats().get('salawat', 0)})


@app.route('/admin')
def admin_page():
    r = app.response_class(ADMIN_HTML, mimetype='text/html')
    r.headers['Cache-Control'] = 'no-store'
    r.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return r


def _media_route(path_name, mimetype, as_attachment=False, download_name=None):
    p = os.path.join(DATA_DIR, path_name)
    if not os.path.exists(p):
        return jsonify({"error": "not found"}), 404
    return send_file(p, mimetype=mimetype, conditional=True, as_attachment=as_attachment,
                     download_name=download_name, max_age=3600)


@app.route('/salawat')
def salawat_audio():
    return _media_route('salawat_custom.mp3', 'audio/mpeg')


@app.route('/app.apk')
def app_apk():
    return _media_route('app_custom.apk', 'application/vnd.android.package-archive', True, 'MODYXBIO.apk')


def _media_admin(filename, kind):
    """kind: audio | apk | image"""
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    path = os.path.join(DATA_DIR, filename)
    if request.method == 'DELETE':
        try:
            os.remove(path)
        except Exception:
            pass
        _logo_cache.clear()
        return jsonify({"ok": True})
    f = request.files.get('file')
    if not f:
        return jsonify({"error": "اختار ملف الأول"}), 400
    if kind == 'audio' and not (f.mimetype or '').startswith('audio'):
        return jsonify({"error": "ملف صوتي فقط (mp3 يفضل)"}), 400
    if kind == 'apk' and not (f.filename or '').lower().endswith('.apk'):
        return jsonify({"error": "ملف APK فقط"}), 400
    if kind == 'image':
        try:
            from PIL import Image
            im = Image.open(f.stream).convert('RGB')
            w, h = im.size
            m = min(w, h)
            im = im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m)).resize(
                (min(m, 768),) * 2, getattr(Image, 'Resampling', Image).LANCZOS)
            im.save(path, 'PNG', optimize=True)
        except Exception:
            return jsonify({"error": "صورة غير صالحة"}), 400
        _logo_cache.clear()
        return jsonify({"ok": True})
    try:
        f.save(path)
    except Exception:
        return jsonify({"error": "تعذر حفظ الملف على السيرفر"}), 500
    return jsonify({"ok": True})


@app.route('/api/admin/salawat', methods=['POST', 'DELETE'])
def admin_salawat():
    return _media_admin('salawat_custom.mp3', 'audio')


@app.route('/api/admin/apk', methods=['POST', 'DELETE'])
def admin_apk():
    return _media_admin('app_custom.apk', 'apk')


@app.route('/api/admin/logo', methods=['POST', 'DELETE'])
def admin_logo():
    return _media_admin('logo_custom.png', 'image')


@app.route('/api/admin/backup')
def admin_backup():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in ('stats.json', 'guestbook.json', 'gallery.json', 'ads.json', 'config.json', 'daily.json'):
            p = os.path.join(DATA_DIR, n)
            if os.path.exists(p):
                z.write(p, n)
    buf.seek(0)
    return send_file(buf, mimetype='application/zip', as_attachment=True,
                     download_name='modyxbio-backup-%s.zip' % time.strftime('%Y%m%d'))


ADMIN_HTML = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#050506">
<title>لوحة التحكم | MODYXBIO</title>
<link rel="icon" href="/icon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800;900&display=swap" rel="stylesheet">
<style>
:root{--bg:#050506;--panel:#0d0d12;--panel2:#09090d;--line:rgba(255,255,255,.09);--red:#ff2b2b;--red2:#a8001a;--gold:#d9b25f;--gold2:#f3dd9b;--txt:#ececf1;--mut:#9a9aaa}
*{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg)}
body{font-family:'Cairo','Segoe UI',sans-serif;color:var(--txt);min-height:100vh;line-height:1.7;
 background:radial-gradient(110% 55% at 50% -6%,rgba(255,43,43,.2),transparent 62%),radial-gradient(90% 50% at 50% 112%,rgba(168,0,26,.26),transparent 66%),var(--bg);background-attachment:fixed}
button,input,select,textarea{font-family:inherit;font-size:.95rem}
:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.hide{display:none!important}

/* ---------- تسجيل الدخول ---------- */
#login{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:22px}
.lbox{width:100%;max-width:400px;text-align:center;padding:34px 26px 28px;border-radius:24px;border:1px solid rgba(217,178,95,.38);
 background:linear-gradient(180deg,rgba(255,255,255,.04),transparent 40%),var(--panel);box-shadow:0 28px 80px rgba(0,0,0,.65),0 0 90px rgba(255,43,43,.12)}
.lbox .lg{width:112px;height:112px;border-radius:50%;border:3px solid rgba(217,178,95,.65);box-shadow:0 0 40px rgba(255,43,43,.4);margin-bottom:14px}
.lbox h1{font-size:1.45rem;font-weight:900;color:#fff}
.lbox p{color:var(--mut);font-size:.88rem;margin:4px 0 20px}
.field{width:100%;padding:13px 14px;border-radius:12px;border:1px solid var(--line);background:#08080c;color:#fff}
.field:focus{border-color:var(--red);box-shadow:0 0 0 3px rgba(255,43,43,.2);outline:none}
textarea.field{resize:vertical;min-height:110px;line-height:1.8}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:11px 18px;border-radius:12px;border:1px solid rgba(255,255,255,.16);cursor:pointer;font-weight:800;color:#fff;
 background:linear-gradient(180deg,#d12424,var(--red2));box-shadow:0 8px 22px rgba(168,0,26,.4),inset 0 1px 0 rgba(255,255,255,.22);transition:transform .15s,box-shadow .15s}
.btn:hover{transform:translateY(-1px)}.btn:active{transform:scale(.97)}
.btn.full{width:100%}
.btn.ghost{background:rgba(217,178,95,.07);border-color:rgba(217,178,95,.5);color:var(--gold2);box-shadow:none}
.btn.dark{background:#16161d;box-shadow:none;color:var(--txt)}
.btn.sm{padding:6px 12px;font-size:.82rem;border-radius:10px}
.msg{min-height:1.6em;margin-top:12px;font-size:.88rem;color:#ff7b7b}

/* ---------- الهيكل ---------- */
.top{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 16px;background:rgba(5,5,7,.88);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid rgba(217,178,95,.25)}
.brand{display:flex;align-items:center;gap:10px;font-weight:900}
.brand img{width:38px;height:38px;border-radius:50%;border:1px solid rgba(217,178,95,.7);box-shadow:0 0 14px rgba(255,43,43,.5)}
.brand small{display:block;font-weight:600;color:var(--mut);font-size:.72rem;line-height:1.2}
.tabs{position:sticky;top:59px;z-index:19;display:flex;gap:6px;overflow-x:auto;padding:10px 16px;background:rgba(5,5,7,.85);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tabs button{flex:0 0 auto;padding:8px 16px;border-radius:30px;border:1px solid var(--line);background:transparent;color:var(--mut);font-weight:700;cursor:pointer;white-space:nowrap}
.tabs button.on{background:linear-gradient(180deg,#d12424,var(--red2));color:#fff;border-color:rgba(255,255,255,.2)}
main{max-width:1000px;margin:0 auto;padding:18px 16px 70px}
.tab{display:none}.tab.on{display:block}
.panel{position:relative;background:linear-gradient(180deg,rgba(255,255,255,.035),transparent 36%),var(--panel);border:1px solid var(--line);border-radius:18px;padding:18px;margin-bottom:16px;box-shadow:0 14px 40px rgba(0,0,0,.4)}
.panel::after{content:"";position:absolute;top:0;left:14%;right:14%;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:.5}
.panel h2{font-size:1.05rem;font-weight:900;margin-bottom:4px;color:#fff}
.panel .sub{color:var(--mut);font-size:.84rem;margin-bottom:12px}
.panel h3{font-size:.95rem;color:var(--gold2);margin:18px 0 6px;font-weight:800}

/* ---------- نظرة عامة ---------- */
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:12px;margin-bottom:16px}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:14px 12px}
.tile b{display:block;font-size:1.7rem;font-weight:900;color:#fff;line-height:1.3}
.tile span{font-size:.8rem;color:var(--mut)}
.tile.gold{border-color:rgba(217,178,95,.5);background:linear-gradient(160deg,rgba(217,178,95,.12),var(--panel) 60%)}
.tile.gold b{color:var(--gold2)}
.bars{display:flex;align-items:flex-end;gap:5px;height:130px;margin-top:8px;direction:ltr}
.bars div{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%;min-width:0}
.bars i{display:block;width:100%;max-width:26px;border-radius:6px 6px 2px 2px;background:linear-gradient(var(--red),var(--red2));min-height:3px}
.bars em{font-style:normal;font-size:.68rem;color:var(--mut);margin-top:4px}
.bars u{text-decoration:none;font-size:.7rem;color:var(--gold2);margin-bottom:2px}
.ratio{height:10px;border-radius:10px;background:#16161d;overflow:hidden;margin:8px 0 4px}
.ratio i{display:block;height:100%;background:linear-gradient(90deg,var(--red2),var(--red),var(--gold))}

/* ---------- نماذج ---------- */
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
label.f{display:block;font-size:.84rem;color:#c9c9d6;font-weight:600}
label.f .field{margin-top:5px;font-weight:400}
.colors{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.colors label{font-size:.78rem;color:var(--mut);text-align:center}
.colors input{width:100%;height:42px;border:1px solid var(--line);border-radius:10px;background:#08080c;padding:3px;cursor:pointer;margin-top:4px}
.chk{display:inline-flex;align-items:center;gap:7px;margin:4px 14px 4px 0;font-size:.86rem;color:#d4d4de;cursor:pointer}
.chk input{accent-color:var(--red);width:17px;height:17px}
.range{width:100%;accent-color:var(--red)}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}

/* ---------- قوائم ---------- */
.list .it{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;background:var(--panel2);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-top:10px}
.it .t{word-break:break-word;font-size:.92rem}
.it small{display:block;color:var(--mut);font-size:.76rem;margin-top:3px}
.empty{color:var(--mut);text-align:center;padding:22px 0;font-size:.9rem}

/* ---------- وسائط ---------- */
.media{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.media .panel{margin:0}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.74rem;font-weight:800;background:#16161d;color:var(--mut);border:1px solid var(--line)}
.badge.ok{background:rgba(217,178,95,.12);color:var(--gold2);border-color:rgba(217,178,95,.45)}
.media img.pv{width:84px;height:84px;border-radius:50%;border:2px solid rgba(217,178,95,.6);display:block;margin:10px 0}
audio{width:100%;margin:10px 0;height:40px}
.up{position:relative;overflow:hidden}
.up input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%}

.toast{position:fixed;left:50%;bottom:calc(20px + env(safe-area-inset-bottom));transform:translate(-50%,30px);opacity:0;pointer-events:none;z-index:99;background:#15151c;border:1px solid rgba(217,178,95,.5);color:#fff;padding:11px 20px;border-radius:14px;font-weight:700;transition:.25s;max-width:90vw;text-align:center}
.toast.on{opacity:1;transform:translate(-50%,0)}
.toast.bad{border-color:#ff5b5b;color:#ffb3b3}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>

<div id="login">
 <div class="lbox">
  <img class="lg" src="/logo.png" alt="MODYXBIO">
  <h1>لوحة التحكم</h1>
  <p>منطقة خاصة بالمطور. أدخل كلمة السر للمتابعة.</p>
  <input id="pw" class="field" type="password" placeholder="كلمة السر" autocomplete="current-password">
  <button class="btn full" id="goBtn" style="margin-top:12px" onclick="login()">دخول</button>
  <div class="msg" id="lmsg"></div>
</div></div>

<div id="app" class="hide">
 <header class="top">
  <div class="brand"><img src="/logo.png" alt=""><div>MODYXBIO<small>لوحة التحكم</small></div></div>
  <div class="row"><a class="btn ghost sm" href="/" target="_blank" rel="noopener">فتح الموقع</a><button class="btn dark sm" onclick="logout()">خروج</button></div>
 </header>
 <nav class="tabs" id="tabs">
  <button data-t="home" class="on">نظرة عامة</button><button data-t="site">إعدادات الموقع</button><button data-t="ads">الإعلانات</button>
  <button data-t="guest">تعليقات الزوار</button><button data-t="gal">المعرض</button><button data-t="media">الوسائط والتطبيق</button><button data-t="sec">الأمان</button>
 </nav>

 <main>
  <!-- نظرة عامة -->
  <section class="tab on" id="t-home">
   <div class="tiles" id="tiles"></div>
   <div class="panel"><h2>الزيارات آخر 14 يوم</h2><div class="sub" id="barsSub"></div><div class="bars" id="bars"></div></div>
   <div class="panel"><h2>نجاح تحديث البايو</h2><div class="ratio"><i id="ratioI" style="width:0"></i></div><div class="sub" id="ratioT"></div></div>
   <div class="panel"><h2>إجراءات سريعة</h2><div class="sub">النسخة الاحتياطية بتشمل الإحصائيات والتعليقات والمعرض والإعلانات والإعدادات.</div>
    <div class="row"><button class="btn" onclick="backup()">تحميل نسخة احتياطية</button><button class="btn dark" onclick="load(true)">تحديث الأرقام</button><button class="btn dark" onclick="resetStats()">تصفير الإحصائيات</button></div></div>
  </section>

  <!-- إعدادات الموقع -->
  <section class="tab" id="t-site">
   <div class="panel"><h2>الهوية والنصوص</h2><div class="sub">اترك أي خانة فاضية لاستخدام النص الافتراضي في الموقع.</div>
    <div class="grid2">
     <label class="f">اسم الموقع<input class="field" id="c_site" placeholder="MODYXBIO"></label>
     <label class="f">الشارة فوق العنوان<input class="field" id="c_eye" placeholder="الشرق الأوسط • ME"></label>
     <label class="f">اسم المطور<input class="field" id="c_dev"></label>
     <label class="f">اسم الشهرة<input class="field" id="c_fms"></label></div>
    <label class="f" style="margin-top:12px">الفقرة التعريفية<textarea class="field" id="c_lead"></textarea></label>
    <h3>التواصل</h3>
    <div class="grid2">
     <label class="f">يوزر تليجرام (من غير @)<input class="field" id="c_tg" placeholder="MODYXBOT1" dir="ltr"></label>
     <label class="f">يوزر تيك توك (من غير @)<input class="field" id="c_tt" placeholder="king_burd" dir="ltr"></label>
     <label class="f">رقم واتساب بالصيغة الدولية<input class="field" id="c_wa" placeholder="201204564384" dir="ltr"></label></div>
    <h3>قسم التطبيق</h3>
    <div class="grid2">
     <label class="f">رابط تحميل التطبيق (اختياري، لو مفيش APK مرفوع)<input class="field" id="c_app" placeholder="https://" dir="ltr"></label>
     <label class="f">نص قسم التطبيق<input class="field" id="c_apt"></label></div>
   </div>
   <div class="panel"><h2>الألوان والشريط</h2>
    <div class="colors">
     <label>الخلفية 1<input type="color" id="c_t1"></label><label>الخلفية 2<input type="color" id="c_t2"></label>
     <label>الأساسي<input type="color" id="c_t3"></label><label>الثانوي<input type="color" id="c_t4"></label></div>
    <div style="margin-top:12px"><label class="chk"><input type="checkbox" id="c_thon"> فرض هذه الألوان على كل الزوار عند الحفظ</label>
     <label class="chk"><input type="checkbox" id="c_ton"> إظهار شريط الإعلانات</label></div>
    <label class="f" style="margin-top:8px">سرعة الشريط (ثواني للدورة، أقل = أسرع)<input class="range" type="range" id="c_tsp" min="10" max="120" value="45"></label>
   </div>
   <div class="panel"><h2>إخفاء أقسام</h2><div id="hidBox"></div></div>
   <div class="panel"><h2>المحتوى</h2><div class="sub">سطر لكل عنصر، والفصل بعلامة |</div>
    <label class="f">المميزات: أيقونة | عنوان | نص<textarea class="field" id="c_fe" dir="auto"></textarea></label>
    <label class="f" style="margin-top:10px">الخطوات: عنوان | نص<textarea class="field" id="c_st" dir="auto"></textarea></label>
    <label class="f" style="margin-top:10px">الأسئلة: سؤال | إجابة<textarea class="field" id="c_fq" dir="auto"></textarea></label>
    <label class="f" style="margin-top:10px">قوالب البايو: اسم | البايو<textarea class="field" id="c_tp" dir="auto"></textarea></label>
   </div>
   <button class="btn full" onclick="saveCfg()">حفظ كل الإعدادات</button>
  </section>

  <!-- الإعلانات -->
  <section class="tab" id="t-ads">
   <div class="panel"><h2>إعلانات الشريط العلوي</h2><div class="sub">سطر لكل إعلان بالشكل: النص | الرابط</div>
    <textarea class="field" id="adsT" dir="ltr" style="min-height:220px"></textarea>
    <button class="btn" style="margin-top:12px" onclick="saveAds()">حفظ الإعلانات</button></div>
  </section>

  <!-- الزوار -->
  <section class="tab" id="t-guest"><div class="panel"><h2>تعليقات الزوار</h2><div class="sub" id="gbSub"></div><div class="list" id="gbList"></div></div></section>

  <!-- المعرض -->
  <section class="tab" id="t-gal"><div class="panel"><h2>معرض البايوهات</h2><div class="sub" id="galSub"></div><div class="list" id="galList"></div></div></section>

  <!-- الوسائط -->
  <section class="tab" id="t-media">
   <div class="media">
    <div class="panel"><h2>لوجو الموقع والتطبيق</h2><div class="sub">بيظهر في الموقع وأيقونة التطبيق وعند مشاركة الرابط.</div>
     <img class="pv" id="logoPv" src="/logo.png" alt="">
     <div class="row"><span class="btn up">رفع لوجو جديد<input type="file" accept="image/*" onchange="upFile(this,'/api/admin/logo','تم تغيير اللوجو')"></span><button class="btn dark" onclick="delFile('/api/admin/logo','رجع اللوجو الأصلي')">الأصلي</button></div></div>
    <div class="panel"><h2>ملف التطبيق APK</h2><div class="sub">لو رفعته، يظهر زر تحميل APK في قسم التطبيق.</div>
     <div id="apkSt"></div>
     <div class="row" style="margin-top:10px"><span class="btn up">رفع APK<input type="file" accept=".apk,application/vnd.android.package-archive" onchange="upFile(this,'/api/admin/apk','تم رفع التطبيق')"></span><button class="btn dark" onclick="delFile('/api/admin/apk','تم حذف الـ APK')">حذف</button></div></div>
    <div class="panel"><h2>صوت الصلاة على النبي ﷺ</h2><div class="sub">لو مفيش ملف مرفوع، الموقع بينطق الصلاة بصوت المتصفح. ارفع تسجيل صوتي لو عايز صوت بعينه.</div>
     <div id="salSt"></div>
     <div class="row" style="margin-top:10px"><span class="btn up">رفع صوت<input type="file" accept="audio/*" onchange="upFile(this,'/api/admin/salawat','تم رفع الصوت')"></span><button class="btn dark" onclick="delFile('/api/admin/salawat','رجع صوت المتصفح')">حذف</button></div></div>
    <div class="panel"><h2>موسيقى الموقع</h2><div class="sub">ملف mp3 لحد 25MB.</div>
     <div id="musSt"></div>
     <div class="row" style="margin-top:10px"><span class="btn up">رفع أغنية<input type="file" accept="audio/*" onchange="upFile(this,'/api/admin/music','تم تغيير الأغنية')"></span><button class="btn dark" onclick="delFile('/api/admin/music','رجعت الأغنية الأصلية')">الأصلية</button></div></div>
   </div>
  </section>

  <!-- الأمان -->
  <section class="tab" id="t-sec">
   <div class="panel"><h2>تغيير كلمة السر</h2><div class="sub">8 حروف على الأقل. بعد التغيير هتحتاج تسجل دخول من جديد.</div>
    <input class="field" id="npw" type="password" placeholder="كلمة السر الجديدة" autocomplete="new-password">
    <button class="btn" style="margin-top:12px" onclick="chPw()">تغيير كلمة السر</button></div>
   <div class="panel"><h2>حماية الدخول</h2><div class="sub">بعد 5 محاولات غلط من نفس الجهاز يتقفل الدخول 10 دقايق. الجلسة بتنتهي تلقائيًا بعد 12 ساعة.</div>
    <button class="btn dark" onclick="logout()">تسجيل الخروج</button></div>
  </section>
 </main>
</div>
<div class="toast" id="toast"></div>

<script>
const $=id=>document.getElementById(id);
const esc=t=>String(t==null?'':t).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const NLC=String.fromCharCode(10);
const SEC={tpl:'القوالب',fmt:'التنسيق',bc:'ألوان البايو',col:'ألوان الموقع',gal:'المعرض',stats:'الإحصائيات',rate:'التقييم',saved:'المحفوظات',hist:'السجل',gb:'دفتر الزوار',share:'المشاركة',msg:'رسالة المطور',font:'مولد الخطوط',grad:'التدرج',sym:'الرموز',img:'البايو كصورة',mus:'المشغل',feat:'المميزات',how:'طريقة الاستخدام',faq:'الأسئلة',app:'تحميل التطبيق'};
let TOK='';try{TOK=sessionStorage.getItem('mx_adm')||''}catch(e){}
let D=null,tt=null;

function toast(m,bad){const t=$('toast');t.textContent=m;t.className='toast on'+(bad?' bad':'');clearTimeout(tt);tt=setTimeout(()=>t.className='toast',2600)}
async function api(p,body,method){
 const o={method:method||(body?'POST':'GET'),headers:{'X-Token':TOK}};
 if(body){o.headers['Content-Type']='application/json';o.body=JSON.stringify(body)}
 const r=await fetch(p,o);let d={};try{d=await r.json()}catch(e){}d._s=r.status;return d}

function show(on){$('login').classList.toggle('hide',on);$('app').classList.toggle('hide',!on)}
async function login(){
 const b=$('goBtn');b.disabled=true;$('lmsg').textContent='';
 try{const d=await api('/api/admin/login',{pass:$('pw').value});
  if(d.token){TOK=d.token;try{sessionStorage.setItem('mx_adm',TOK)}catch(e){}$('pw').value='';await load();}
  else $('lmsg').textContent=d.error||'تعذر الدخول'}
 catch(e){$('lmsg').textContent='حصلت مشكلة في الاتصال'}
 b.disabled=false}
function logout(){TOK='';try{sessionStorage.removeItem('mx_adm')}catch(e){}show(false)}
$('pw').addEventListener('keydown',e=>{if(e.key==='Enter')login()});

document.querySelectorAll('#tabs button').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('#tabs button').forEach(x=>x.classList.toggle('on',x===b));
 document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on',x.id==='t-'+b.dataset.t));window.scrollTo(0,0)});

async function load(quiet){
 if(!TOK){show(false);return}
 const d=await api('/api/admin/summary');
 if(d._s===403||d.error){logout();if(!quiet)toast('الجلسة انتهت، سجّل دخول تاني',1);return}
 D=d;show(true);renderAll();if(quiet===true)toast('تم تحديث الأرقام')}

function fmt(n){return Number(n||0).toLocaleString('ar-EG')}
function size(b){return b>1048576?(b/1048576).toFixed(1)+' MB':Math.round(b/1024)+' KB'}

function renderAll(){renderHome();renderSite();renderAds();renderGuest();renderGal();renderMedia()}

function renderHome(){
 const s=D.stats||{},c=D.counts||{};
 const avg=s.rate_n?(s.rate_sum/s.rate_n).toFixed(1):'—';
 const T=[['الزوار',fmt(s.visits)],['تحديثات ناجحة',fmt(s.updates)],['تحديثات فاشلة',fmt(s.failed)],['صلّوا على النبي ﷺ',fmt(s.salawat),1],['متوسط التقييم',avg+(s.rate_n?'  ('+fmt(s.rate_n)+')':'')],['تعليقات الزوار',fmt(c.guest)],['بايوهات المعرض',fmt(c.gallery)]];
 $('tiles').innerHTML=T.map(t=>'<div class="tile'+(t[2]?' gold':'')+'"><b>'+t[1]+'</b><span>'+t[0]+'</span></div>').join('');
 const dl=D.daily||[],mx=Math.max(1,...dl.map(x=>x.n));
 $('bars').innerHTML=dl.map(x=>'<div title="'+esc(x.d)+'"><u>'+(x.n||'')+'</u><i style="height:'+Math.max(3,Math.round(x.n/mx*100))+'%"></i><em>'+esc(x.d.slice(8))+'</em></div>').join('');
 const tot=dl.reduce((a,x)=>a+x.n,0);$('barsSub').textContent='إجمالي آخر 14 يوم: '+fmt(tot)+' زيارة';
 const u=s.updates||0,f=s.failed||0,p=u+f?Math.round(u/(u+f)*100):0;
 $('ratioI').style.width=p+'%';$('ratioT').textContent=u+f?('نسبة النجاح '+p+'٪ من '+fmt(u+f)+' محاولة'):'لسه مفيش محاولات'}

function renderSite(){
 const c=D.cfg||{},th=c.default_theme||['#050506','#14060a','#ff2b2b','#a8001a'],hid=c.hidden||[];
 const set=(id,v)=>{$(id).value=v||''};
 set('c_site',c.site_name);set('c_eye',c.hero_eyebrow);set('c_lead',c.hero_lead);set('c_dev',c.dev_name);set('c_fms',c.dev_fms);
 set('c_tg',c.tg_user);set('c_tt',c.tt_user);set('c_wa',c.wa_num);set('c_app',c.app_url);set('c_apt',c.app_text);
 ['c_t1','c_t2','c_t3','c_t4'].forEach((id,i)=>$(id).value=th[i]);
 $('c_thon').checked=!!c.default_theme;$('c_ton').checked=c.ticker_on!==false;$('c_tsp').value=c.ticker_speed||45;
 $('hidBox').innerHTML=Object.keys(SEC).map(k=>'<label class="chk"><input type="checkbox" class="hid" value="'+k+'" '+(hid.includes(k)?'checked':'')+'> '+SEC[k]+'</label>').join('');
 const L=a=>(a||[]).map(r=>r.join(' | ')).join(NLC);
 set('c_fe',L(c.feats));set('c_st',L(c.steps));set('c_fq',L(c.faqs));set('c_tp',L(c.tpls))}

function sp(l,n){const p=[];let r=l;for(let i=0;i<n-1;i++){const k=r.indexOf('|');if(k<0)break;p.push(r.slice(0,k).trim());r=r.slice(k+1)}p.push(r.trim());return p}
async function saveCfg(){
 const g=id=>$(id).value.trim();
 const o={site_name:g('c_site'),hero_eyebrow:g('c_eye'),hero_lead:g('c_lead'),dev_name:g('c_dev'),dev_fms:g('c_fms'),tg_user:g('c_tg'),tt_user:g('c_tt'),wa_num:g('c_wa'),app_url:g('c_app'),app_text:g('c_apt'),
  ticker_on:$('c_ton').checked,ticker_speed:+$('c_tsp').value,hidden:[...document.querySelectorAll('.hid:checked')].map(x=>x.value)};
 if($('c_thon').checked)o.default_theme=['c_t1','c_t2','c_t3','c_t4'].map(i=>$(i).value);
 const P=(id,n)=>g(id).split(NLC).map(l=>sp(l,n)).filter(a=>a.length===n&&a[0]);
 [['feats','c_fe',3],['steps','c_st',2],['faqs','c_fq',2],['tpls','c_tp',2]].forEach(x=>{const r=P(x[1],x[2]);if(r.length)o[x[0]]=r});
 const d=await api('/api/admin/config',o);
 if(d.ok){toast('تم حفظ الإعدادات');load(1)}else toast(d.error||'حصلت مشكلة',1)}

function renderAds(){
 const a=D.ads;
 $('adsT').value=(a||[]).map(x=>x[0]+' | '+x[1]).join(NLC)}
async function saveAds(){
 const ads=$('adsT').value.split(NLC).map(l=>{const i=l.lastIndexOf('|');return i>0?[l.slice(0,i).trim(),l.slice(i+1).trim()]:[l.trim(),'#']}).filter(a=>a[0]);
 const d=await api('/api/admin/ads',{ads:ads});
 if(d.ok){toast('تم حفظ '+d.count+' إعلان')}else toast('حصلت مشكلة',1)}

function renderGuest(){
 const l=D.guest||[];$('gbSub').textContent=(D.counts&&D.counts.guest||0)+' تعليق';
 $('gbList').innerHTML=l.length?l.map(x=>'<div class="it"><div class="t">'+esc(x.text)+'<small>'+esc(x.name)+' • '+new Date(x.t).toLocaleString('ar-EG')+'</small></div><button class="btn sm dark" onclick="delGb('+x.id+')">حذف</button></div>').join(''):'<div class="empty">مفيش تعليقات لسه</div>'}
async function delGb(id){if(!confirm('حذف التعليق؟'))return;await api('/api/admin/guest/delete',{id:id});load(1)}

function renderGal(){
 const l=D.gallery||[];$('galSub').textContent=(D.counts&&D.counts.gallery||0)+' بايو (بيظهر آخر 50)';
 $('galList').innerHTML=l.length?l.map(x=>'<div class="it"><div class="t">'+esc(x.bio)+'<small>إعجابات '+(x.likes||0)+' • استخدامات '+(x.uses||0)+'</small></div><button class="btn sm dark" onclick="delGal('+x.id+')">حذف</button></div>').join(''):'<div class="empty">المعرض فاضي</div>'}
async function delGal(id){if(!confirm('حذف البايو من المعرض؟'))return;await api('/api/admin/gallery/delete',{id:id});load(1)}

function renderMedia(){
 const f=D.files||{},v=Date.now();
 $('logoPv').src='/logo.png?v='+v;
 $('apkSt').innerHTML=f.apk?'<span class="badge ok">مرفوع</span> '+size(f.apk)+' <a class="btn ghost sm" href="/app.apk">تجربة التحميل</a>':'<span class="badge">مفيش ملف</span>';
 $('salSt').innerHTML=f.salawat?'<span class="badge ok">صوت مخصص</span><audio controls preload="none" src="/salawat?v='+v+'"></audio>':'<span class="badge">صوت المتصفح (افتراضي)</span>';
 $('musSt').innerHTML=f.music?'<span class="badge ok">أغنية مخصصة</span><audio controls preload="none" src="/music?v='+v+'"></audio>':'<span class="badge">الأغنية الأصلية</span>'}
async function upFile(inp,url,okMsg){
 const f=inp.files[0];if(!f)return;const fd=new FormData();fd.append('file',f);toast('جاري الرفع...');
 try{const r=await fetch(url,{method:'POST',headers:{'X-Token':TOK},body:fd});let d={};try{d=await r.json()}catch(e){}
  if(d.ok){toast(okMsg);load(1)}else toast(d.error||'فشل الرفع',1)}catch(e){toast('فشل الرفع',1)}
 inp.value=''}
async function delFile(url,okMsg){const d=await api(url,null,'DELETE');if(d.ok){toast(okMsg);load(1)}else toast(d.error||'حصلت مشكلة',1)}

async function backup(){
 try{const r=await fetch('/api/admin/backup',{headers:{'X-Token':TOK}});if(!r.ok)throw 0;const b=await r.blob();
  const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='modyxbio-backup.zip';document.body.appendChild(a);a.click();a.remove();toast('تم تحميل النسخة')}catch(e){toast('تعذر تحميل النسخة',1)}}
async function resetStats(){if(!confirm('تصفير كل الإحصائيات؟ (عداد الصلاة على النبي بيفضل زي ما هو)'))return;const d=await api('/api/admin/reset',{});if(d.ok){toast('تم التصفير');load(1)}}
async function chPw(){
 const d=await api('/api/admin/password',{pass:$('npw').value});
 if(d.ok){toast('تم تغيير كلمة السر');$('npw').value='';setTimeout(logout,1200)}else toast(d.error||'حصلت مشكلة',1)}

if(TOK)load(1);else show(false);
</script>
</body>
</html>
'''

# اللوجو مدمج في الملف (JPEG 512px). لو حطيت logo_custom.png جنب الملف أو رفعته من لوحة التحكم هيتستخدم بدله.
LOGO_B64 = (
    "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"
    "iIjP4XO9FV9w8J948qi3sPyr7r87Q3voziJYt559CfIn1Ei75n1/zjKD1zz33eY7LwD1jxiJ4qzW1a9PRytyPK/Rugx6GzbHkbfR"
    "5nT4O7g3YOf3NnktLmejxTtOU61Tn8vSzunwZ2obcFiBxFomTQwl0MzRp35rFS/A/VydbL0825Ubfm1M2Wonv2cPFpxXKrZYIK1K"
    "SRdSj3XJk80tb1nnNbxSXpeZ1PmCPTfDfc/Mocv7zk0onnO98S9/q8y6SzYSvjkdBXqfZ+fwItyvMneTXqF1/E1vQLnnnrsx4Rox"
    "aWHp2+X37fN72T0dLMp133c10V+fN1Ob278mfT3riKjo8OurUQ7/AJCVLcufdFU1KC0LCS/HLJayM/Raga+UurkzU67cGpRz9F1W"
    "7Utz1/QaPL7eV2XPZMCZGC1uz1vyX6BtTmvLreQbd7luqh6h4T1PJS9a6HwRU93zObuw9H2vMuVT6BwMGhn1ZN+1fjT0nxroMSaQ"
    "eiclNTsi57op67ct0kdK3PfnzKWXfrVsuTTjIJWbeUmjTWvRBLEX5N2LHMfTlYSb+ZHNA+JuwvtYevm3JGIjryTXwfmT17YAF+Qc"
    "0idegmrj7OTF1OGhlnoIujxsbSzN0pZ9nKrprWs/HVQVJqbOOpKsVvPrrWn1K7pNUTTk17fOux9HrYuXM+3Xt88m3m6y47otbnzm"
    "2y1a1QNCTKE6b8lItswZoWa4acSOFnJiOWYFlhGzwuGaeWtOjRqy3cvSzYZWa+bLebTp3V0DbyQAAB2tjy07LVXayqdUDHmvlscl"
    "6NICZlOmuNffkYPSYbPBoV3vXY7nJ9VUr9R0iPLGyY+vi3k0Ov04eGWv0jfEZ0nLpdP6FwCYU9F4dWtHtxpxTdjnPLTqIovzy3um"
    "TxcfS7SPPJpkRn1tXNVYyU14YhzEAPi1lpXz7ZZaurGiZL478wBflAAABUDR0uf2Of36EF+K/HSuwWlZI9OHL08cczbxohUvzS3a"
    "F3L0e+9I8r9Iy93u+F9H+cuzw8jmLseNPd8rTxejzZ+m4HYPRfO6Mpx/pOVUhT6mjxp3ODN5aevZejVO0y7vKy6DPu0zjd3l60Op"
    "wdLjjH0827z+lTc1NeBGqTV6xpF9Agfh6g6XMvkIGvmgAAAAAASxLFukzam3z/Q5LHWtPN3qGhW5vpM7J6/ldfLhbepbeO25SkV3"
    "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"
    "WeZeL/kuXLf+T//Z"
)

if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG') == '1', host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))