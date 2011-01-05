import random
import string


POPULATION = list(string.ascii_letters) + range(10)


def get_random_token():
  """Return random 32 chars string to be used as a short living token.
  """
  return ''.join([str(random.choice(POPULATION)) for i in xrange(32)])

