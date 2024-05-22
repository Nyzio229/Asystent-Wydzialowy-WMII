using Android.App;
using Android.Runtime;
using Microsoft.Maui.Controls.Compatibility.Platform.Android;

namespace WMiIApp
{
    [Application]
    public class MainApplication : MauiApplication
    {
        public MainApplication(IntPtr handle, JniHandleOwnership ownership)
            : base(handle, ownership)
        {
            Microsoft.Maui.Handlers.EditorHandler.Mapper.AppendToMapping("EditorCustomization", (handler, view) =>
            {
                handler.PlatformView.BackgroundTintList = Android.Content.Res.ColorStateList.ValueOf(Color.FromRgba("#3F4152").ToAndroid());
                handler.PlatformView.TextCursorDrawable.SetTint(Colors.White.ToAndroid());
            });
            Microsoft.Maui.Handlers.EntryHandler.Mapper.AppendToMapping("EntryCustomization", (handler, view) =>
            {
                handler.PlatformView.BackgroundTintList = Android.Content.Res.ColorStateList.ValueOf(Color.FromRgba("#3F4152").ToAndroid());
                handler.PlatformView.TextCursorDrawable.SetTint(Colors.White.ToAndroid());
            });
        }

        protected override MauiApp CreateMauiApp() => MauiProgram.CreateMauiApp();
    }
}
