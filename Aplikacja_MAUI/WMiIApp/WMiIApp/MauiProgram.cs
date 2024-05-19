using Microsoft.Extensions.Logging;
using WMiIApp.ViewModels;
using WMiIApp.Services;
using CommunityToolkit.Maui;
using banditoth.MAUI.DeviceId;

namespace WMiIApp
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            var builder = MauiApp.CreateBuilder();
            builder
                .UseMauiApp<App>()
                .UseMauiCommunityToolkit()
                .ConfigureDeviceIdProvider()
                .ConfigureFonts(fonts =>
                {
                    fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                    fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
                });
#if DEBUG
            builder.Logging.AddDebug();
#endif
            builder.Services.AddSingleton<MainPage>();
            builder.Services.AddSingleton<MessageService>();
            builder.Services.AddSingleton<MainViewModel>();
            builder.Services.AddSingleton<EmployeesPage>();
            builder.Services.AddSingleton<EmployeesViewModel>();
            return builder.Build();
        }
    }
}
