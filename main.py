from os import path, makedirs
from pydantic import BaseModel
from typing import Dict
import pendulum
import aiohttp
import asyncio
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt

URLs = [
    "https://api.blockchain.com/v3/exchange/tickers/BTC-USD",
    "https://api.blockchain.com/v3/exchange/tickers/ETH-USD"
]

class Data(BaseModel):
    date: str
    price: float

async def fetch(url: str) -> Dict[str, float]:
    """
    Fetches data from the given URL using aiohttp.

    Args:
        url (str): The URL to fetch data from.

    Returns:
        dict: A dictionary containing the fetched data.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return {"date": pendulum.now().to_date_string(), "price": data["price_24h"]}

def append_data_to_csv(data: Data, filename: str) -> None:
    """
    Appends the given data to a CSV file.

    Args:
        data (Data): The data to append to the CSV file.
        filename (str): The path to the CSV file.
    """
    df_fetched = pd.DataFrame([data.model_dump()])
    if path.exists(filename):
        df_loaded = pd.read_csv(filename)
        df = pd.concat([df_fetched, df_loaded], ignore_index=True)
    else:
        df = df_fetched
    df.to_csv(filename, index=False)

def load_csv(filename: str) -> pd.DataFrame:
    """
    Loads data from a CSV file.

    Args:
        filename (str): The path to the CSV file.

    Returns:
        pandas.DataFrame: The loaded data as a DataFrame.
    """
    if path.exists(filename):
        df = pd.read_csv(filename).sort_index(ascending=False).head(7)
    else:
        df = pd.DataFrame()
    return df

def create_plot(df: pd.DataFrame, currency: str) -> None:
    """
    Creates a plot of the price data.

    Args:
        df (pandas.DataFrame): The DataFrame containing the price data.
        currency (str): The currency symbol.

    Returns:
        None
    """
    plt.style.use('Solarize_Light2')
    plt.figure(figsize=(12,5))
    plt.xlabel('Date')
    plt.ylabel('Price USD')
    if currency == 'BTC-USD':
        plt.plot(df['date'], df['price'], 
            linestyle='solid',
            color='Orange',
            marker="H",
            markeredgecolor = "black",
            markerfacecolor='green',
            markeredgewidth=2,
            markersize=3,
            linewidth=4,
            alpha=0.5)
    elif currency == 'ETH-USD':
        plt.plot(df['date'], df['price'], 
            linestyle='solid',
            color='Blue',
            marker="H",
            markeredgecolor = "black",
            markerfacecolor='green',
            markeredgewidth=2,
            markersize=3,
            linewidth=4,
            alpha=0.5)
    plt.title(f'7 days Price {currency}')
    plt.savefig(f'./img/{currency.lower()}.png')

def generate_readme(data: Dict[str, float]) -> None:
    """
    Generates a README file using a Jinja2 template.

    Args:
        data (dict): The data to be rendered in the template.

    Returns:
        None
    """
    loader = FileSystemLoader('./templates')
    env = Environment(loader=loader)
    template = env.get_template('readme.md')
    with open('README.md', 'w') as f:
        f.write(template.render(data))

def main() -> None:
    """
    The main function that orchestrates the data fetching, processing, plotting, and README generation.

    Returns:
        None
    """
    if not path.exists("data"):
        makedirs("data")
    if not path.exists("img"):
        makedirs("img")
    data = {}
    for URL in URLs:
        name = URL.split("/")[-1]
        jsonData = asyncio.run(fetch(URL))
        data[name.split("-")[0]] = jsonData['price']
        append_data_to_csv(Data(**jsonData), f"./data/{name.lower()}.csv")
        df = load_csv(f"./data/{name.lower()}.csv")
        create_plot(df, name)
    generate_readme(data)

if __name__ == "__main__":
    main()

