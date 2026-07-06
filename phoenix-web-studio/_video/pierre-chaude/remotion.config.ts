import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// H.264 MP4 — lecture universelle (Reels / TikTok / QuickTime)
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
