import discord
from discord.ext import commands
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from redbot.core import commands as rbc

class RadarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @rbc.command()
    async def radar(self, ctx, economic: int, social: int, environmental: int, geopolitical: int):
        # Define the dimensions and labels for the four axes
        labels = ['Economic', 'Social', 'Environmental', 'Geopolitical']
        dimensions = len(labels)

        # Create an array with the scale for each axis
        scale = np.array([100, 100, 100, 100])

        # Create a function to plot the four-axis radar chart
        async def plot_radar(ctx, values):
            angles = np.linspace(0, 2*np.pi, dimensions, endpoint=False)
            values = np.concatenate((values,[values[0]]))
            angles = np.concatenate((angles,[angles[0]+0.1]))

            fig = plt.figure()
            ax = fig.add_subplot(111, polar=True)
            ax.plot(angles, values, 'o-', linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            ax.set_thetagrids(np.degrees(angles), labels)
            ax.set_rlim(0, max(scale))

            # Save the plot to a bytes buffer
            buffer = BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            # Send the plot as an attachment in Discord
            file = discord.File(buffer, filename='radar.png')
            await ctx.send(file=file)

        # Call the function to plot the radar chart
        await plot_radar(ctx, [economic, social, environmental, geopolitical])
