import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Camera, CheckCircle2, Loader2, User } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation } from "wouter";

type CaptureStep = "front-ready" | "front-countdown" | "front-captured" | "side-ready" | "side-countdown" | "side-captured" | "processing" | "complete";

export default function Capture() {
  const [, setLocation] = useLocation();
  const [step, setStep] = useState<CaptureStep>("front-ready");
  const [countdown, setCountdown] = useState(10);
  const [frontPhoto, setFrontPhoto] = useState<string | null>(null);
  const [sidePhoto, setSidePhoto] = useState<string | null>(null);

  const progress = 
    step === "front-ready" ? 15 : 
    step === "front-countdown" ? 25 : 
    step === "front-captured" ? 40 :
    step === "side-ready" ? 50 :
    step === "side-countdown" ? 65 :
    step === "side-captured" ? 75 :
    step === "processing" ? 90 : 100;

  // Countdown timer effect
  useEffect(() => {
    if (step === "front-countdown" || step === "side-countdown") {
      if (countdown > 0) {
        const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
        return () => clearTimeout(timer);
      } else {
        // Capture photo when countdown reaches 0
        if (step === "front-countdown") {
          setFrontPhoto("captured");
          setStep("front-captured");
          setCountdown(10); // Reset for next countdown
        } else if (step === "side-countdown") {
          setSidePhoto("captured");
          setStep("side-captured");
          setCountdown(10);
          // Start processing
          setTimeout(() => {
            setStep("processing");
            setTimeout(() => {
              setStep("complete");
              setTimeout(() => {
                setLocation("/results");
              }, 1500);
            }, 2000);
          }, 500);
        }
      }
    }
  }, [step, countdown, setLocation]);

  const handleStartFrontCapture = () => {
    setCountdown(10);
    setStep("front-countdown");
  };

  const handleStartSideCapture = () => {
    setCountdown(10);
    setStep("side-countdown");
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </Link>
          <div className="flex-1 max-w-md mx-4">
            <Progress value={progress} className="h-2" />
          </div>
          <div className="text-sm text-gray-600 font-medium">
            {progress}%
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          {/* Front Photo - Ready */}
          {step === "front-ready" && (
            <Card className="border-2">
              <CardHeader className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <User className="h-8 w-8 text-blue-600" />
                </div>
                <CardTitle className="text-2xl">Front Photo Setup</CardTitle>
                <CardDescription className="text-base">
                  Position yourself for the front-facing photo
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Camera Preview Placeholder */}
                <div className="aspect-[3/4] bg-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-48 h-96 border-2 border-dashed border-blue-400 rounded-full opacity-50" />
                  </div>
                  <div className="relative z-10 text-white text-center space-y-2">
                    <Camera className="h-16 w-16 mx-auto opacity-50" />
                    <p className="text-sm">Camera preview will appear here</p>
                  </div>
                </div>

                {/* Instructions */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-3">Positioning Instructions:</h4>
                  <ul className="text-sm text-blue-800 space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">1.</span>
                      <span>Stand 6-8 feet away from the camera</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">2.</span>
                      <span><strong>Press your legs out</strong> and stand with feet shoulder-width apart</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">3.</span>
                      <span><strong>Place your arms slightly away from your body</strong> at about 30-45 degrees</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">4.</span>
                      <span>Face directly toward the camera</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">5.</span>
                      <span>Ensure good lighting and your full body is in frame</span>
                    </li>
                  </ul>
                </div>

                <Button 
                  size="lg" 
                  className="w-full text-lg py-6"
                  onClick={handleStartFrontCapture}
                >
                  <Camera className="mr-2 h-5 w-5" />
                  Start 10-Second Countdown
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Front Photo - Countdown */}
          {step === "front-countdown" && (
            <Card className="border-2 border-blue-500">
              <CardContent className="py-16 text-center space-y-8">
                <div className="space-y-4">
                  <div className="text-8xl font-bold text-blue-600 animate-pulse">
                    {countdown}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900">Get Ready!</h3>
                  <p className="text-gray-600 max-w-md mx-auto">
                    Position yourself with legs pressed out, arms at 30-45° from your body, facing the camera
                  </p>
                </div>

                {/* Visual Guide */}
                <div className="aspect-[3/4] max-w-xs mx-auto bg-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-32 h-64 border-2 border-dashed border-blue-400 rounded-full opacity-50 animate-pulse" />
                  </div>
                  <div className="relative z-10 text-white">
                    <User className="h-24 w-24 mx-auto opacity-70" />
                  </div>
                </div>

                <div className="text-sm text-gray-500">
                  Photo will be captured automatically in {countdown} seconds
                </div>
              </CardContent>
            </Card>
          )}

          {/* Front Photo - Captured */}
          {step === "front-captured" && (
            <Card className="border-2 border-green-200 bg-green-50">
              <CardContent className="py-12 text-center space-y-6">
                <CheckCircle2 className="h-20 w-20 text-green-600 mx-auto" />
                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-gray-900">Front Photo Captured!</h3>
                  <p className="text-gray-600">
                    Great! Now let's capture your side profile
                  </p>
                </div>
                <Button 
                  size="lg" 
                  className="mt-4"
                  onClick={() => setStep("side-ready")}
                >
                  Continue to Side Photo
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Side Photo - Ready */}
          {step === "side-ready" && (
            <Card className="border-2">
              <CardHeader className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <User className="h-8 w-8 text-purple-600" />
                </div>
                <CardTitle className="text-2xl">Side Photo Setup</CardTitle>
                <CardDescription className="text-base">
                  Rotate 90° to your right for the side profile photo
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Camera Preview Placeholder */}
                <div className="aspect-[3/4] bg-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-48 h-96 border-2 border-dashed border-purple-400 rounded-full opacity-50" />
                  </div>
                  <div className="relative z-10 text-white text-center space-y-2">
                    <Camera className="h-16 w-16 mx-auto opacity-50" />
                    <p className="text-sm">Camera preview will appear here</p>
                  </div>
                </div>

                {/* Success indicator for front photo */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                  <span className="text-sm text-green-800 font-medium">Front photo captured successfully</span>
                </div>

                {/* Instructions */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-semibold text-purple-900 mb-3">Positioning Instructions:</h4>
                  <ul className="text-sm text-purple-800 space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">1.</span>
                      <span><strong>Turn 90° to your right</strong> (your right side faces the camera)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">2.</span>
                      <span>Stand with feet together or slightly apart</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">3.</span>
                      <span><strong>Place your arms relaxed at your sides</strong></span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">4.</span>
                      <span>Stand up straight with good posture</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold mt-0.5">5.</span>
                      <span>Keep your full body in frame from head to toe</span>
                    </li>
                  </ul>
                </div>

                <Button 
                  size="lg" 
                  className="w-full text-lg py-6"
                  onClick={handleStartSideCapture}
                >
                  <Camera className="mr-2 h-5 w-5" />
                  Start 10-Second Countdown
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Side Photo - Countdown */}
          {step === "side-countdown" && (
            <Card className="border-2 border-purple-500">
              <CardContent className="py-16 text-center space-y-8">
                <div className="space-y-4">
                  <div className="text-8xl font-bold text-purple-600 animate-pulse">
                    {countdown}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900">Get Ready!</h3>
                  <p className="text-gray-600 max-w-md mx-auto">
                    Stand sideways with arms relaxed at your sides, good posture, facing right
                  </p>
                </div>

                {/* Visual Guide */}
                <div className="aspect-[3/4] max-w-xs mx-auto bg-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-32 h-64 border-2 border-dashed border-purple-400 rounded-full opacity-50 animate-pulse" />
                  </div>
                  <div className="relative z-10 text-white">
                    <User className="h-24 w-24 mx-auto opacity-70" />
                  </div>
                </div>

                <div className="text-sm text-gray-500">
                  Photo will be captured automatically in {countdown} seconds
                </div>
              </CardContent>
            </Card>
          )}

          {/* Side Photo - Captured */}
          {step === "side-captured" && (
            <Card className="border-2 border-green-200 bg-green-50">
              <CardContent className="py-12 text-center space-y-6">
                <CheckCircle2 className="h-20 w-20 text-green-600 mx-auto" />
                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-gray-900">Side Photo Captured!</h3>
                  <p className="text-gray-600">
                    Perfect! Processing your measurements now...
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Processing */}
          {step === "processing" && (
            <Card className="border-2">
              <CardContent className="py-16 text-center space-y-6">
                <Loader2 className="h-16 w-16 animate-spin text-blue-600 mx-auto" />
                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-gray-900">Processing Your Measurements</h3>
                  <p className="text-gray-600">
                    Our AI is analyzing your photos to extract precise body measurements...
                  </p>
                </div>
                <div className="max-w-md mx-auto space-y-2 text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span>Photos captured</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                    <span>Detecting pose landmarks...</span>
                  </div>
                  <div className="flex items-center gap-2 opacity-50">
                    <span className="h-4 w-4" />
                    <span>Calculating measurements</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Complete */}
          {step === "complete" && (
            <Card className="border-2 border-green-200 bg-green-50">
              <CardContent className="py-16 text-center space-y-6">
                <CheckCircle2 className="h-20 w-20 text-green-600 mx-auto" />
                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-gray-900">Measurements Complete!</h3>
                  <p className="text-gray-600">
                    Redirecting you to your results...
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}

