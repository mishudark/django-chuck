#!chuck_extends project/settings/common.py

#!chuck_appends SETTINGS

import mongoengine
mongoengine.connect('$PROJECT_NAME')

SESSION_ENGINE = 'mongoengine.django.sessions'

# In case you want to use the MongoDB's GridFS feature for storage
# purposes uncomment the following 2 lines:
#   from mongoengine.django.storage import GridFSStorage
#   fs = GridFSStorage()

#!end


#!chuck_appends AUTHENTICATION_BACKENDS
    'mongoengine.django.auth.MongoEngineBackend',
#!end
