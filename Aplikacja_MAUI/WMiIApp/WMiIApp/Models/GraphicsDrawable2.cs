using Microsoft.Maui.Graphics;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class GraphicsDrawable2 : IDrawable
    {
        public void Draw(ICanvas canvas, RectF dirtyRect)
        {
            if (App.pathFinder.Path == null || App.pathFinder.Path.Count == 0)
                return;


            // Tworzymy liste par (x, y) dla punktow na ścieżce
            var points = new List<Tuple<float, float>>();

            // Przechodzimy po kazdym pokoju w sciezce
            foreach (var room in (App.pathFinder.Path))
            {
                // Sprawdzamy, czy pokoj należy do poziomu 2
                if (room.Floor == 2)
                {
                    // Dodajemy pare (x, y) do listy punktow
                    points.Add(new Tuple<float, float>((float)room.PositionX, (float)room.PositionY));
                }
            }

            // Rysujemy linie laczace punkty na sciezce
            for (int i = 0; i < points.Count - 1; i++)
            {
                canvas.StrokeColor = Colors.Chocolate;
                canvas.StrokeSize = (float)1.5;

                var startPoint = points[i];
                var endPoint = points[i + 1];

                canvas.DrawLine(startPoint.Item1, startPoint.Item2, endPoint.Item1, endPoint.Item2);


                canvas.StrokeColor = Colors.Chocolate;
                canvas.StrokeSize = 1;
                DrawArrow(canvas, startPoint.Item1, startPoint.Item2, endPoint.Item1, endPoint.Item2);
            }

            // Kolor punktu startowego
            canvas.StrokeColor = Colors.Green;
            canvas.StrokeSize = 2;

            // Sprawdzamy czy pokoj startowy nalezy do poziomu 2
            if (App.pathFinder.Path[0].Floor == 2)
            {
                canvas.DrawCircle((float)App.pathFinder.Path[0].PositionX, (float)App.pathFinder.Path[0].PositionY, (float)1.5);
                canvas.FillCircle((float)App.pathFinder.Path[0].PositionX, (float)App.pathFinder.Path[0].PositionY, (float)1.1);
            }

            // Kolor punktu startowego
            canvas.StrokeColor = Colors.Red;
            canvas.StrokeSize = 2;

            // Sprawdzamy czy pokoj docelowy nalezy do poziomu 2
            if (App.pathFinder.Path[App.pathFinder.Path.Count() - 1].Floor == 2)
            {
                canvas.DrawCircle((float)App.pathFinder.Path[App.pathFinder.Path.Count() - 1].PositionX, (float)App.pathFinder.Path[App.pathFinder.Path.Count() - 1].PositionY, (float)1.5);
                canvas.FillCircle((float)App.pathFinder.Path[App.pathFinder.Path.Count() - 1].PositionX, (float)App.pathFinder.Path[App.pathFinder.Path.Count() - 1].PositionY, (float)1.1);
            }
        }

        // Metoda do rysowania strzalki
        private void DrawArrow(ICanvas canvas, float startX, float startY, float endX, float endY)
        {
            float arrowSize = (float)5; // Rozmiar strzalki

            // Obliczamy kat miedzy punktami
            float angle = (float)Math.Atan2(endY - startY, endX - startX);

            // Obliczamy wspolrzedne koncow strzalki
            float arrowEndX1 = endX - arrowSize * (float)Math.Cos(angle + Math.PI / 6);
            float arrowEndY1 = endY - arrowSize * (float)Math.Sin(angle + Math.PI / 6);
            float arrowEndX2 = endX - arrowSize * (float)Math.Cos(angle - Math.PI / 6);
            float arrowEndY2 = endY - arrowSize * (float)Math.Sin(angle - Math.PI / 6);

            // Rysujemy dwie linie tworzace strzalke
            canvas.DrawLine(endX, endY, arrowEndX1, arrowEndY1);
            canvas.DrawLine(endX, endY, arrowEndX2, arrowEndY2);
        }
    }
}
