using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using ServerApiMikoAI;
using ServerApiMikoAI.Controllers;
using ServerApiMikoAI.Models.Context;
using System.Reflection;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();
builder.Services.AddHttpClient();
builder.Services.AddDbContext<PostrgeSQLContext>(opt => opt.UseNpgsql(builder.Configuration.GetConnectionString("QuestionDB")));
builder.Services.AddDbContext<VerificationDataBaseContext>(opt => opt.UseNpgsql(builder.Configuration.GetConnectionString("VerificationDB")));
builder.Services.AddScoped<AuthorizationService>();

var connStringEmp = builder.Configuration.GetConnectionString("EmployeesDB");
builder.Services.AddDbContext<WMiIEmployeesDatabase>(opt => {
    opt.UseMySql(connStringEmp, ServerVersion.AutoDetect(connStringEmp));
});

var connStringPln = builder.Configuration.GetConnectionString("PlansDB");
builder.Services.AddDbContext<WMiIPlansDatabase>(opt => {
    opt.UseMySql(connStringPln, ServerVersion.AutoDetect(connStringPln));
});

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "ServerApiMikoAI", Version = "v1" });
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    c.IncludeXmlComments(xmlPath);
    c.OperationFilter<RequireRequestBodyFilter>();
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger(c => {
        c.SerializeAsV2 = true;
    }
    );
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
