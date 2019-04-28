package com.kjlee.rtsp.rtp.packets;

import com.kjlee.rtsp.rtsp.RtpFrame;

/**
 * Created by pedro on 7/11/18.
 */

public interface VideoPacketCallback {
  void onVideoFrameCreated(RtpFrame rtpFrame);
}
