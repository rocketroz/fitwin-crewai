import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Download, Ruler, Share2 } from "lucide-react";
import { Link } from "wouter";

export default function Results() {
  // TODO: Get actual measurements from API
  const measurements = {
    height_cm: 170.0,
    chest_cm: 100.0,
    waist_natural_cm: 81.3,
    hip_low_cm: 100.0,
    inseam_cm: 76.0,
    shoulder_cm: 45.0,
    sleeve_cm: 60.0,
  };

  const recommendations = [
    { category: "Tops", size: "M", confidence: 0.92 },
    { category: "Bottoms", size: "32", confidence: 0.88 },
    { category: "Dresses", size: "8", confidence: 0.85 },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Home
            </Button>
          </Link>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Download
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-8">
        <div className="container mx-auto px-4 max-w-5xl space-y-8">
          {/* Success Message */}
          <div className="text-center space-y-2">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <Ruler className="h-8 w-8 text-green-600" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
              Your Measurements Are Ready!
            </h1>
            <p className="text-gray-600 text-lg">
              Here are your precise body measurements and size recommendations
            </p>
          </div>

          {/* Size Recommendations */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle className="text-2xl">Size Recommendations</CardTitle>
              <CardDescription>
                Based on your measurements, here are your recommended sizes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {recommendations.map((rec) => (
                  <div
                    key={rec.category}
                    className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6 text-center space-y-2"
                  >
                    <h3 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">
                      {rec.category}
                    </h3>
                    <div className="text-4xl font-bold text-blue-600">
                      {rec.size}
                    </div>
                    <div className="text-sm text-gray-600">
                      {Math.round(rec.confidence * 100)}% confidence
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Detailed Measurements */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle className="text-2xl">Detailed Measurements</CardTitle>
              <CardDescription>
                All measurements are in centimeters (cm)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {Object.entries(measurements).map(([key, value]) => {
                  const label = key
                    .replace(/_cm$/, "")
                    .split("_")
                    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(" ");
                  
                  return (
                    <div
                      key={key}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border"
                    >
                      <span className="font-medium text-gray-700">{label}</span>
                      <span className="text-xl font-bold text-blue-600">
                        {value.toFixed(1)} cm
                      </span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Metadata */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="py-4">
              <div className="flex flex-wrap gap-6 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Source:</span> MediaPipe Web
                </div>
                <div>
                  <span className="font-medium">Accuracy:</span> ~95%
                </div>
                <div>
                  <span className="font-medium">Model:</span> v1.0-mediapipe
                </div>
                <div>
                  <span className="font-medium">Date:</span> {new Date().toLocaleDateString()}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* CTA */}
          <div className="text-center space-y-4">
            <p className="text-gray-600">
              Want to measure again or try a different pose?
            </p>
            <Link href="/capture">
              <Button size="lg">
                <Ruler className="mr-2 h-5 w-5" />
                Take New Measurements
              </Button>
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm py-6 mt-8">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          <p>All measurements are processed securely on your device using MediaPipe technology.</p>
        </div>
      </footer>
    </div>
  );
}

