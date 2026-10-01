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

app = Flask(__name__)

# HTML from user (with minor adjustments for Flask)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
<title>MODYXBIO | محرر البايو - الشرق الأوسط ME</title>
<meta name="theme-color" content="var(--a)" id="themeColorMeta">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
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
</style>
</head>
<body>

<!-- ===== CAPTCHA OVERLAY - ALWAYS SHOWN ON PAGE LOAD ===== -->
<div id="captchaOverlay">
    <div class="captcha-box">
        <div class="robot-icon">🤖</div>
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
    <h1>🐉 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</h1>
    <div class="subtitle">
        <span class="api-badge">⚡ Credit by 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 🇪🇬</span>
    </div>
    <div class="devbox"><div><span>𝑫𝒆𝒗:</span> 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅</div><div><span>𝑭𝑴𝑺:</span> 𝒁𝑨𝑨𝑻𝑨𝑹</div></div>
    <div class="links" style="text-align:center; margin-bottom:12px;">
        <a href="https://t.me/MODYXBOT1" target="_blank"><i class="fab fa-telegram"></i> تليجرام</a>
        <a href="https://www.tiktok.com/@king_burd" target="_blank"><i class="fab fa-tiktok"></i> تيك توك</a><a href="https://wa.me/201204564384" target="_blank"><i class="fab fa-whatsapp"></i> واتساب</a>
    </div>
    
    <div class="card">
        <h3>✏️ محرر البايو</h3>
        <textarea id="bio" placeholder="اكتب البايو بتاعك هنا..."></textarea>
        <div id="charCount" style="text-align:right; font-size:12px; margin-top:5px;">0 / 250</div>
        <div class="preview" id="preview">معاينة مباشرة</div>
        <div style="margin-top:8px"><button class="format-btn" onclick="copyBio($('bio').value)">📋 نسخ</button><button class="format-btn" onclick="shareBio()">🔗 مشاركة</button><button class="format-btn" onclick="saveBio()">💾 حفظ</button></div>
    </div>

    <div class="card">
        <h3>⚡ قوالب بايو جاهزة (اضغط واستخدم)</h3>
        <div class="chips" id="tpls"></div>
    </div>

    <div class="card">
        <h3>🎨 التنسيق</h3>
        <button class="format-btn" onclick="insertSimple('[b]')">عريض</button>
        <button class="format-btn" onclick="insertSimple('[i]')">مائل</button>
        <button class="format-btn" onclick="insertSimple('[c]')">منحني</button>
        <button class="format-btn" onclick="insertSimple('[u]')">تحته خط</button>
        <button class="format-btn" onclick="insertSimple('[s]')">مشطوب</button>
    </div>

    <div class="card">
        <h3>🌈 ألوان البايو (كل ألوان العالم)</h3>
        <div class="colors-ribbon" id="colorRibbon"></div>
    </div>



    <div class="card">
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
    <div class="card">
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

    <div class="card"><h3>🌍 معرض البايوهات العام</h3>
        <div class="tabs"><button class="format-btn" id="tNew" onclick="galSort('new')">🕒 الأحدث</button><button class="format-btn off" id="tTop" onclick="galSort('top')">🔥 الأكثر إعجاباً</button></div>
        <div id="galList"></div>
    </div>
    <div class="card"><h3>📊 إحصائيات الموقع</h3><div class="stats"><div><b id="stV">0</b><small>👁️ زوار الموقع</small></div><div><b id="stU">0</b><small>✅ تحديثات ناجحة</small></div><div><b id="stM">0</b><small>🙋 تحديثاتك أنت</small></div></div></div>
    <div class="card" style="text-align:center"><h3>⭐ قيّم الموقع</h3><div id="stars"></div><div style="font-size:.9rem;margin-top:4px">المتوسط: <b id="avg">—</b></div></div>
    <div class="card"><h3>💾 بايوهاتي المحفوظة</h3><div id="savedList"></div></div>
    <div class="card"><h3>🕘 سجل التحديثات</h3><div id="histList"></div><button class="format-btn" onclick="clearHist()" style="margin-top:10px">🗑️ مسح السجل</button></div>

    <div class="card"><h3>📖 دفتر الزوار</h3>
        <input id="gbName" placeholder="اسمك" maxlength="30">
        <textarea id="gbText" placeholder="اكتب تعليقك هنا..." maxlength="200" style="height:80px"></textarea>
        <button class="format-btn" onclick="gbSend()" style="margin-top:8px">📨 إرسال التعليق</button>
        <div id="gbList"></div>
    </div>

    <div class="card" style="text-align:center"><h3>📣 شارك الموقع</h3>
        <div id="shr" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center"></div>
    </div>

    <div class="card"><h3>✉️ ابعت رسالة للمطور</h3>
        <input id="mName" placeholder="اسمك (اختياري)">
        <textarea id="mText" placeholder="اكتب رسالتك..." style="height:90px"></textarea>
        <div style="margin-top:8px"><button class="sb" style="background:#25D366" onclick="msgTo('wa')"><i class="fab fa-whatsapp"></i> واتساب</button> <button class="sb" style="background:#229ED9" onclick="msgTo('tg')"><i class="fab fa-telegram"></i> تليجرام</button> <button class="sb" style="background:#000;border:2px solid #fe2c55" onclick="msgTo('tt')"><i class="fab fa-tiktok"></i> تيك توك</button></div>
        <div style="font-size:.75rem;color:#aaa;margin-top:6px">في تليجرام وتيك توك الرسالة بتتنسخ تلقائي، والصقها في المحادثة.</div>
    </div>

    <div class="card" style="text-align:center">
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
    <div class="foot">© جميع الحقوق محفوظة — 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶 🇪🇬 • 𝑫𝒆𝒗: 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅<br><a href="#" onclick="admOpen();return false" style="color:#888;font-size:.7rem;text-decoration:none">🔐 لوحة المطور</a></div>
</div>

<button id="langBtn" onclick="toggleLang()">🌐 EN</button>
<div class="modal" id="adm"><div class="mbox">
 <div id="admLogin"><h3>🔐 لوحة المطور</h3><input id="admPass" type="password" placeholder="كلمة السر"><button class="format-btn" style="width:100%;margin-top:10px" onclick="admLogin()">دخول</button></div>
 <div id="admPanel" style="display:none">
  <h3>📊 ملخص</h3><div id="admStats" class="item"></div>
  <h3 style="margin-top:12px">📢 إعلانات الشريط (سطر لكل إعلان: النص | الرابط)</h3>
  <textarea id="admAds" style="height:140px;direction:ltr"></textarea>
  <button class="format-btn" onclick="admSaveAds()">💾 حفظ الإعلانات</button>
  <h3 style="margin-top:12px">💬 تعليقات الزوار</h3><div id="admGb"></div>
  <h3 style="margin-top:12px">🌍 المعرض العام</h3><div id="admGal"></div>
  <button class="format-btn" onclick="admReset()" style="margin-top:10px">♻️ تصفير الإحصائيات</button>
 </div>
 <button class="format-btn" onclick="admClose()" style="width:100%;margin-top:12px;background:#444;color:#fff">إغلاق</button>
</div></div>
<div id="ticker"><div id="tk"></div></div>
<div id="loader"><div class="lg">𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</div><div class="lbar"><div id="lfill"></div></div><div id="lpct">0%</div><div id="ltxt">جاري التحميل...</div></div>
<div id="welcome" class="gate-w" style="position:fixed;inset:0;background:rgba(0,0,0,.94);backdrop-filter:blur(26px);display:flex;justify-content:center;align-items:center;padding:20px">
 <div class="captcha-box" style="animation:none">
  <div class="ttlogo"><i class="fab fa-tiktok"></i></div>
  <h2>أهلاً بك في 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶</h2>
  <div style="font-size:.8rem;color:#ddd;margin-bottom:8px">𝑫𝒆𝒗: 𝑯𝒂𝒎𝒆𝒅 𝒂𝒍𝒔𝒉𝒉𝒂𝒕 𝑯𝒂𝒎𝒆𝒅 • 𝑭𝑴𝑺: 𝒁𝑨𝑨𝑻𝑨𝑹</div>
  <p class="sub-text">تابعني على تيك توك الأول عشان توصلك كل الجديد 🔥<br>وبعدها اضغط دخول</p>
  <a class="big" href="https://www.tiktok.com/@king_burd" target="_blank" rel="noopener"><i class="fab fa-tiktok"></i> صفحتي على تيك توك</a>
  <button class="big" id="enterBtn">🚀 دخول الموقع</button>
 </div>
</div>
<audio id="bgm" src="/music" loop preload="auto" autoplay></audio>
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
function applyT(b1,b2,a,a2,tc){const r=document.documentElement.style;r.setProperty('--b1',b1);r.setProperty('--b2',b2);r.setProperty('--a',a);r.setProperty('--a2',a2);
tc=tc||a;$('themeColorMeta').content=tc;$('c1').value=b1;$('c2').value=b2;$('c3').value=a;$('c5').value=a2;$('c4').value=tc;
try{localStorage.setItem('mx_theme',JSON.stringify([b1,b2,a,a2,tc]))}catch(e){}}
TH.forEach(t=>{const d=document.createElement('div');d.className='th';d.style.background='linear-gradient(135deg,'+t[0]+','+t[1]+','+t[2]+')';
d.onclick=()=>{document.querySelectorAll('.th').forEach(x=>x.classList.remove('on'));d.classList.add('on');stopRainbow();applyT(...t)};$('themes').appendChild(d)});
['c1','c2','c3','c5','c4'].forEach(id=>$(id).addEventListener('input',()=>applyT($('c1').value,$('c2').value,$('c3').value,$('c5').value,$('c4').value)));
function randomTheme(){stopRainbow();const h=Math.random()*360;applyT(hx(h,70,6),hx((h+40)%360,60,16),hx((h+180)%360,100,60),hx((h+220)%360,100,60))}
let rb=null,hue=0;function stopRainbow(){if(rb){clearInterval(rb);rb=null;$('rbBtn').style.opacity=1}}
function toggleRainbow(){if(rb)return stopRainbow();$('rbBtn').style.opacity=.6;rb=setInterval(()=>{hue=(hue+2)%360;const a=hx(hue,100,60);const r=document.documentElement.style;
r.setProperty('--a',a);r.setProperty('--a2',hx((hue+60)%360,100,60));r.setProperty('--b1',hx(hue,60,6));r.setProperty('--b2',hx((hue+30)%360,55,15));$('themeColorMeta').content=a},60)}
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
for(let i=0;i<4;i++){const o=document.createElement('div');o.className='orb';const z=180+Math.random()*200;o.style.cssText='width:'+z+'px;height:'+z+'px;left:'+Math.random()*60+'vw;top:'+Math.random()*60+'vh;animation-duration:'+(14+Math.random()*14)+'s;animation-delay:-'+Math.random()*10+'s';document.body.appendChild(o)}
// أثر المؤشر
let lt=0;addEventListener('pointermove',e=>{const n=Date.now();if(n-lt<40)return;lt=n;const d=document.createElement('div');d.className='tr';d.style.left=e.clientX-4+'px';d.style.top=e.clientY-4+'px';document.body.appendChild(d);
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
function rs(){rc.width=innerWidth;rc.height=innerHeight;dr=Array.from({length:Math.min(380,Math.floor(innerWidth/2.5))},()=>({x:Math.random()*rc.width,y:Math.random()*rc.height,l:rnd(14,34),v:rnd(16,30)}))}rs();addEventListener('resize',rs);
(function rd(){requestAnimationFrame(rd);if(fc++%20===0)rcol=getComputedStyle(document.documentElement).getPropertyValue('--a').trim()||'#0ff';
rx.clearRect(0,0,rc.width,rc.height);rx.strokeStyle=rcol;rx.globalAlpha=.5;rx.lineWidth=1.4;rx.beginPath();
dr.forEach(d=>{rx.moveTo(d.x,d.y);rx.lineTo(d.x-d.l*.25,d.y+d.l);d.y+=d.v;d.x-=d.v*.25;if(d.y>rc.height){d.y=-40;d.x=Math.random()*(rc.width+250)}});rx.stroke();
if(flash>0){rx.globalAlpha=flash;rx.fillStyle='#fff';rx.fillRect(0,0,rc.width,rc.height);flash-=.05}else if(Math.random()<.0007)flash=.3})();
// الثيم الافتراضي = طوكيو نيون
TH[0]=["#05051a","#1b0a40","#00f0ff","#ff2bd6"];
try{if(localStorage.getItem('mx_v')!=='3'){applyT(...TH[0]);localStorage.setItem('mx_v','3')}}catch(e){}
// شاشة التحميل
(function(){const m=['جاري تحميل الموقع...','تجهيز الأدوات...','تحميل الموسيقى...','تشغيل نظام الحماية...','جاهز 🚀'];let p=0;const iv=setInterval(()=>{p+=Math.random()*9+3;if(p>=100){p=100;clearInterval(iv);setTimeout(()=>{$('loader').classList.add('off');setTimeout(()=>$('loader').remove(),800)},300)}
$('lfill').style.width=p+'%';$('lpct').textContent=Math.floor(p)+'%';$('ltxt').textContent=m[Math.min(4,Math.floor(p/21))]},110)})();
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
const EN_RAW=`أهلاً بك في 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶|Welcome to 𝑴𝑶𝑫𝒀𝑿𝑩𝑰𝑶
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
🌍 المعرض العام|🌍 Public gallery`;
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
function buildTk(){const h=ADS.map(a=>'<a href="'+esc(a[1])+'" target="_blank" rel="noopener">'+esc(a[0])+'</a><span>✦</span>').join('');$('tk').innerHTML=h+h+h+h}
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
if(k==='wa'){open('https://wa.me/201204564384?text='+enc(full),'_blank')}else{open(k==='tg'?'https://t.me/MODYXBOT1':'https://www.tiktok.com/@king_burd','_blank');copyBio(full)}}
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
    return jsonify(_bump('visits'))

@app.route('/api/stats')
def api_stats():
    return jsonify(_load_stats())

# ===== كلمة سر لوحة المطور: غيّرها من هنا أو بمتغير بيئة ADMIN_PASS =====
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'ChangeMe123')
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
_tokens = set()
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

def _is_admin():
    return request.headers.get('X-Token', '') in _tokens

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

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    if _limit('login', 2):
        return jsonify({"error": "استنى ثانيتين وحاول تاني"}), 429
    d = request.get_json(silent=True) or {}
    if hmac.compare_digest(str(d.get('pass', '')), ADMIN_PASS):
        tok = secrets.token_hex(16)
        _tokens.add(tok)
        return jsonify({"token": tok})
    return jsonify({"error": "❌ كلمة السر غلط"}), 403

@app.route('/api/admin/summary')
def admin_summary():
    if not _is_admin():
        return jsonify({"error": "unauthorized"}), 403
    g = _jload('guestbook.json', [])
    return jsonify({"stats": _load_stats(), "guest": list(reversed(g))[:50], "ads": _jload('ads.json', None), "gallery": [_pub(x) for x in reversed(_jload('gallery.json', []))][:50]})

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
    _jsave('stats.json', {"visits": 0, "updates": 0, "failed": 0})
    return jsonify({"ok": True})

@app.route('/music')
def music():
    return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music.mp3'), mimetype='audio/mpeg', conditional=True)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/update', methods=['POST'])
def update_bio():
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)