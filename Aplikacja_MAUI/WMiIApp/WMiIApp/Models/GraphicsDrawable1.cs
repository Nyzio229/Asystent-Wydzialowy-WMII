using Microsoft.Maui.Graphics;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class GraphicsDrawable1 : IDrawable
    {
        public void Draw(ICanvas canvas, RectF dirtyRect)
        {
            if (App.pathFinder.Path == null || App.pathFinder.Path.Count == 0)
                return;

            canvas.StrokeColor = Colors.Chocolate;
            canvas.StrokeSize = 3;

            // Tworzymy listę par (x, y) dla punktów na ścieżce
            var points = new List<Tuple<float, float>>();

            // Przechodzimy po każdym pokoju w ścieżce
            foreach (var room in (App.pathFinder.Path))
            {
                // Sprawdzamy, czy pokój należy do poziomu 1
                if (room.Floor == 1)
                {
                    // Dodajemy parę (x, y) do listy punktów
                    points.Add(new Tuple<float, float>((float)room.PositionX, (float)room.PositionY));
                }
            }

            // Rysujemy linie łączące punkty na ścieżce
            for (int i = 0; i < points.Count - 1; i++)
            {
                var startPoint = points[i];
                var endPoint = points[i + 1];
                canvas.DrawLine(startPoint.Item1, startPoint.Item2, endPoint.Item1, endPoint.Item2);
            }
        }
    }
}
