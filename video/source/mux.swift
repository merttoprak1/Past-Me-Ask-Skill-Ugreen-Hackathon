// Encode a folder of JPEG frames plus a WAV file into an H.264/AAC MP4 with AVFoundation.
// usage: mux <framesDir> <fps> <audio.wav> <out.mp4>
import Foundation
import AVFoundation
import CoreGraphics
import ImageIO

let args = CommandLine.arguments
guard args.count == 5, let fps = Int32(args[2]) else { print("usage: mux <framesDir> <fps> <audio.wav> <out.mp4>"); exit(2) }
let framesDir = args[1], audioPath = args[3], outPath = args[4]
let files = try FileManager.default.contentsOfDirectory(atPath: framesDir).filter { $0.hasSuffix(".jpg") }.sorted()
let outURL = URL(fileURLWithPath: outPath)
try? FileManager.default.removeItem(at: outURL)
let W = 1920, H = 1080

let writer = try AVAssetWriter(outputURL: outURL, fileType: .mp4)
writer.shouldOptimizeForNetworkUse = true
let vIn = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H,
    AVVideoColorPropertiesKey: [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
                                AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
                                AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2],
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 10_000_000,
                                      AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
                                      AVVideoMaxKeyFrameIntervalKey: 60]])
vIn.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: vIn, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
    kCVPixelBufferWidthKey as String: W, kCVPixelBufferHeightKey as String: H])
writer.add(vIn)

let aAsset = AVURLAsset(url: URL(fileURLWithPath: audioPath))
guard let aTrack = aAsset.tracks(withMediaType: .audio).first else { print("no audio track"); exit(1) }
let reader = try AVAssetReader(asset: aAsset)
let rOut = AVAssetReaderTrackOutput(track: aTrack, outputSettings: [
    AVFormatIDKey: kAudioFormatLinearPCM, AVLinearPCMBitDepthKey: 16, AVLinearPCMIsFloatKey: false,
    AVLinearPCMIsBigEndianKey: false, AVLinearPCMIsNonInterleaved: false])
reader.add(rOut)
var acl = AudioChannelLayout()
acl.mChannelLayoutTag = kAudioChannelLayoutTag_Stereo
let aIn = AVAssetWriterInput(mediaType: .audio, outputSettings: [
    AVFormatIDKey: kAudioFormatMPEG4AAC, AVNumberOfChannelsKey: 2, AVSampleRateKey: 44100,
    AVEncoderBitRateKey: 256_000,
    AVChannelLayoutKey: Data(bytes: &acl, count: MemoryLayout<AudioChannelLayout>.size)])
aIn.expectsMediaDataInRealTime = false
writer.add(aIn)

guard writer.startWriting() else { print("startWriting failed: \(String(describing: writer.error))"); exit(1) }
reader.startReading()
writer.startSession(atSourceTime: .zero)

let cs = CGColorSpace(name: CGColorSpace.sRGB)!
let group = DispatchGroup()
var idx = 0
group.enter()
vIn.requestMediaDataWhenReady(on: DispatchQueue(label: "video")) {
    while vIn.isReadyForMoreMediaData {
        if idx >= files.count { vIn.markAsFinished(); group.leave(); return }
        autoreleasepool {
            let url = URL(fileURLWithPath: framesDir).appendingPathComponent(files[idx])
            guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
                  let img = CGImageSourceCreateImageAtIndex(src, 0, nil),
                  let pool = adaptor.pixelBufferPool else { fatalError("frame \(files[idx])") }
            var pb: CVPixelBuffer?
            CVPixelBufferPoolCreatePixelBuffer(nil, pool, &pb)
            let buf = pb!
            CVPixelBufferLockBaseAddress(buf, [])
            let ctx = CGContext(data: CVPixelBufferGetBaseAddress(buf), width: W, height: H, bitsPerComponent: 8,
                                bytesPerRow: CVPixelBufferGetBytesPerRow(buf), space: cs,
                                bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue)!
            ctx.draw(img, in: CGRect(x: 0, y: 0, width: W, height: H))
            CVPixelBufferUnlockBaseAddress(buf, [])
            if !adaptor.append(buf, withPresentationTime: CMTime(value: CMTimeValue(idx), timescale: fps)) {
                fatalError("append failed at \(idx): \(String(describing: writer.error))")
            }
        }
        idx += 1
    }
}
group.enter()
aIn.requestMediaDataWhenReady(on: DispatchQueue(label: "audio")) {
    while aIn.isReadyForMoreMediaData {
        if let sb = rOut.copyNextSampleBuffer() { aIn.append(sb) } else { aIn.markAsFinished(); group.leave(); return }
    }
}
group.wait()
let sem = DispatchSemaphore(value: 0)
writer.finishWriting { sem.signal() }
sem.wait()
if writer.status == .completed { print("ok \(files.count) frames -> \(outPath)") } else { print("failed: \(String(describing: writer.error))"); exit(1) }
