This directory contains project requirements exported in the plain
`requirements.txt` format.

Although we use Poetry to manage project dependencies, it presents challenges
on setting up up-to-date requirements inside a Docker image. To overcome this
inconvenience, we export the list of dependencies to `requirements.txt` and
import the file into the Docker image.
