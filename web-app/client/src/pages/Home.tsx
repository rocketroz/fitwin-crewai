import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Camera, Ruler, Smartphone, Zap } from "lucide-react";
import { Link } from "wouter";
import { APP_TITLE } from "@/const";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Ruler className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">{APP_TITLE}</h1>
          </div>
          <nav className="flex gap-4">
            <Link href="/capture">
              <Button>Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-4xl md:text-6xl font-bold text-gray-900 leading-tight">
                Accurate Body Measurements
                <br />
                <span className="text-blue-600">Right in Your Browser</span>
              </h2>
              <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto">
                Get precise body measurements using AI-powered pose estimation. 
                No app download required. Works on any device with a camera.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/capture">
                <Button size="lg" className="text-lg px-8 py-6">
                  <Camera className="mr-2 h-5 w-5" />
                  Start Measuring
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6">
                Learn More
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap justify-center gap-8 pt-8 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-green-600" />
                <span>Free to use</span>
              </div>
              <div className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-blue-600" />
                <span>Privacy-first</span>
              </div>
              <div className="flex items-center gap-2">
                <Smartphone className="h-5 w-5 text-purple-600" />
                <span>Works on all devices</span>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="container mx-auto px-4 py-16 bg-white/50 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto">
            <h3 className="text-3xl font-bold text-center mb-12 text-gray-900">
              How It Works
            </h3>
            <div className="grid md:grid-cols-3 gap-8">
              <Card className="border-2 hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <Camera className="h-6 w-6 text-blue-600" />
                  </div>
                  <CardTitle>1. Capture Photos</CardTitle>
                  <CardDescription>
                    Take two photos (front and side) using your device camera with real-time guidance
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="border-2 hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                    <Zap className="h-6 w-6 text-purple-600" />
                  </div>
                  <CardTitle>2. AI Processing</CardTitle>
                  <CardDescription>
                    Our AI analyzes your pose and extracts precise body measurements using MediaPipe
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card className="border-2 hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                    <Ruler className="h-6 w-6 text-green-600" />
                  </div>
                  <CardTitle>3. Get Results</CardTitle>
                  <CardDescription>
                    Receive accurate measurements and personalized size recommendations instantly
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-4 py-16">
          <Card className="max-w-3xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 border-0 text-white">
            <CardHeader className="text-center space-y-4 py-12">
              <CardTitle className="text-3xl md:text-4xl">
                Ready to Get Your Perfect Fit?
              </CardTitle>
              <CardDescription className="text-blue-100 text-lg">
                Join thousands of users who found their perfect size with FitTwin
              </CardDescription>
              <div className="pt-4">
                <Link href="/capture">
                  <Button size="lg" variant="secondary" className="text-lg px-8 py-6">
                    Start Measuring Now
                  </Button>
                </Link>
              </div>
            </CardHeader>
          </Card>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm py-8">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          <p>© 2025 FitTwin. All measurements processed securely on your device.</p>
          <div className="flex justify-center gap-6 mt-4">
            <a href="#" className="hover:text-blue-600 transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

