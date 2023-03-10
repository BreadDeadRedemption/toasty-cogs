import discord
from discord.ext import commands
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from redbot.core import commands


class RadarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def fouraxisradar(self, ctx, economic: int, diplomatic: int, civil: int, societal: int):
        # Define the dimensions and labels for the four axes
        labels = ['Economic', 'Diplomatic', 'Civil', 'Societal']
        dimensions = len(labels)

        # Create an array with the scale for each axis
        scale = np.array([100, 100, 100, 100])

        # Create a function to plot the four-axis radar chart
        async def plot_radar(ctx, values):
            angles = np.linspace(0, 2*np.pi, dimensions, endpoint=False)[:-1]
            # Remove the line that concatenates values with [values[0]]
            # values = np.concatenate((values,[values[0]]))
            angles = np.concatenate((angles,[angles[0]]))

            fig = plt.figure()
            ax = fig.add_subplot(111, polar=True)
            ax.plot(angles, values, 'o-', linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            ax.set_thetagrids(angles * 180/np.pi, labels)
            ax.set_rlim(0, max(scale))

            # Save the plot to a bytes buffer
            buffer = BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            # Send the plot as an attachment in Discord
            file = discord.File(buffer, filename='radar.png')
            await ctx.send(file=file)


        # Call the plot_radar function to create and send the chart
        values = [economic, diplomatic, civil, societal]
        await plot_radar(ctx, values)
