class ValidateOnSaveMixin(object):
  """This Mixin ensures that model field validatation happens upon save, which
	is surprisingly not the default action in Django."""

  def save(self, force_insert=False, force_update=False, **kwargs):
    if not (force_insert or force_update):
      self.full_clean()
    super(ValidateOnSaveMixin, self).save(force_insert, force_update, **kwargs)


def number_of_hours(percentage, total_hours):
  return (percentage / 100) * total_hours
