using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp
{
    public class PinchToZoomContainer : ContentView
    {
        double currentScale = 1;
        double startScale = 1;
        double xOffset = 0;
        double yOffset = 0;
        double previousWidth = 0;
        double previousHeight = 0;

        public PinchToZoomContainer()
        {
            PinchGestureRecognizer pinchGesture = new PinchGestureRecognizer();
            pinchGesture.PinchUpdated += OnPinchUpdated;
            GestureRecognizers.Add(pinchGesture);

            // Dodajemy gest przeciagania
            var panGesture = new PanGestureRecognizer();
            panGesture.PanUpdated += OnPanUpdated;
            GestureRecognizers.Add(panGesture);

            SizeChanged += (sender, e) =>
            {
                if (Content != null)
                {
                    double screenWidth = Width;
                    double screenHeight = Height;
                    Content.WidthRequest = screenWidth;
                    Content.HeightRequest = screenHeight;
                }
            };
        }
       

        void OnPinchUpdated(object sender, PinchGestureUpdatedEventArgs e)
        {
            if (e.Status == GestureStatus.Started)
            {
                // Zapisujemy biezacy wspolczynnik skalowania zerujemy składowe dla punktu centralnego transformacji
                startScale = Content.Scale;
                Content.AnchorX = 0;
                Content.AnchorY = 0;
            }
            if (e.Status == GestureStatus.Running)
            {
                // Oblicz wspolczynnik skalowania
                currentScale += (e.Scale - 1) * startScale;
                currentScale = Math.Max(1, currentScale);

                // Wspolrzedna X
                double renderedX = Content.X + xOffset;
                double deltaX = renderedX / Width;
                double deltaWidth = Width / (Content.Width * startScale);
                double originX = (e.ScaleOrigin.X - deltaX) * deltaWidth;

                // Wspolrzedna Y.
                double renderedY = Content.Y + yOffset;
                double deltaY = renderedY / Height;
                double deltaHeight = Height / (Content.Height * startScale);
                double originY = (e.ScaleOrigin.Y - deltaY) * deltaHeight;

                // Oblicz przekształcone wspolrzedne elementu
                double targetX = xOffset - (originX * Content.Width) * (currentScale - startScale);
                double targetY = yOffset - (originY * Content.Height) * (currentScale - startScale);

                // Zastosuj translacje na podstawie zmiany pochodzenia
                Content.TranslationX = Math.Clamp(targetX, -Content.Width * (currentScale - 1), 0);
                Content.TranslationY = Math.Clamp(targetY, -Content.Height * (currentScale - 1), 0);

                // Zastosuj wspolczynnik skalowania
                Content.Scale = currentScale;
            }
            if (e.Status == GestureStatus.Completed)
            {
                // Zapisz delte translacji elementu
                xOffset = Content.TranslationX;
                yOffset = Content.TranslationY;
            }
        }

        void OnPanUpdated(object sender, PanUpdatedEventArgs e)
        {
            if (currentScale > 1 && (e.StatusType == GestureStatus.Running || e.StatusType == GestureStatus.Completed))
            {
                    // Interpolacja pozycji obrazka z użyciem mnoznika
                    double multiplier = 0.5; // Mnoznik interpolacji
                    double deltaX = e.TotalX * multiplier;
                    double deltaY = e.TotalY * multiplier;

                    // Przesun obraz o przesuniecie z uwzglednieniem interpolacji
                    Content.TranslationX = Math.Clamp(Content.TranslationX + deltaX, -Content.Width * (currentScale - 1), 0);
                    Content.TranslationY = Math.Clamp(Content.TranslationY + deltaY, -Content.Height * (currentScale - 1), 0);
            }
        }

        protected override void OnSizeAllocated(double width, double height)
        {
            base.OnSizeAllocated(width, height);

            if (previousWidth != width || previousHeight != height)
            {
                previousWidth = width;
                previousHeight = height;

                UpdateContentScale();
            }
        }

        void UpdateContentScale()
        {
            double newScale = Math.Min(Width / Content.Width, Height / Content.Height);

            // Jesli obraz jest mniejszy niz ekran, powieksz go do odpowiedniego rozmiaru
            if (newScale > 1)
                newScale = Math.Max(Width / Content.Width, Height / Content.Height);

            // Dodatkowy mnoznik
            double additionalScaleFactor = 1.3;

            currentScale = newScale * additionalScaleFactor;
            startScale = newScale * additionalScaleFactor;

            Content.Scale = currentScale;
            Content.TranslationX = 40;
            Content.TranslationY = 100;
            xOffset = 0;
            yOffset = 0;
        }



    }
}
