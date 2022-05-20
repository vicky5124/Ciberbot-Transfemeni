# Ciberbot Transfemení

Documentation:

- [lightbulb](https://hikari-lightbulb.readthedocs.io/en/latest/)
- [hikari](https://davfsa.github.io/hikari-docs/stable/)
- [cassandra](https://docs.datastax.com/en/developer/python-driver/3.25/)

## Running the bot (First time)

- First, you'll need to create a venv with `python3.10 -m venv .venv`, and join the newly created venv with `source .venv/bin/activate`.
- Install all the python dependencies with `pip install -r requirements.txt`
- Download and run the latest version 4 of
[ScyllaDB](https://www.scylladb.com/download/#open-source).
If you are a Windows or MacOS user, you'd need to use
[Cassandra](https://cassandra.apache.org/_/download.html)
along with
[Java 13 (JRE)](https://adoptopenjdk.net/releases.html?variant=openjdk13&jvmVariant=hotspot)
instead.\
Or with docker: `docker run --name scylla-ciber --hostname scylla-ciber -p 9042:9042 --restart=unless-stopped -d scylladb/scylla --smp 1`
- Download
[Lavalink.jar](https://ci.fredboat.com/viewLog.html?buildId=lastSuccessful&buildTypeId=Lavalink_Build&tab=artifacts&guest=1),
[Java 13 (JRE)](https://adoptopenjdk.net/archive.html?variant=openjdk13&jvmVariant=hotspot)
and the configuration file
[application.yml](https://raw.githubusercontent.com/freyacodes/Lavalink/master/LavalinkServer/application.yml.example) (Right click and "Save page as...").
Proceed by renaming `jdk-13.0.2+8-jre` to `jre13` and run `./jre13/bin/java -jar Lavalink.jar`.\
Or with docker: `docker run --name lavalink-ciber -p 2333:2333 -d -v $PWD/application.yml:/opt/Lavalink/application.yml --restart=unless-stopped fredboat/lavalink:dev`
- Create the configuration file based on the example: `cp Config.toml.example Config.toml` and modify it with whichever text editor you like.
- Run the bot with `python start.py`

## Running the bot (Future times)

```bash
source .venv/bin/activate

# If you did the manual install.
./jre13/bin/java -jar Lavalink.jar
# If you used docker.
docker start scylla-ciber lavalink-ciber

# The database can take a bit to start.
# You can skip this and just keep running the bot every 10 seconds until it doesn't show any errors.
sleep 40

python start.py
```
