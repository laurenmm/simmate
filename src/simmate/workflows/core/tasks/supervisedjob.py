# -*- coding: utf-8 -*-

import os
import time
from shutil import make_archive
from subprocess import Popen
from tempfile import TemporaryDirectory

from prefect import Task
from prefect.utilities.tasks import defaults_from_attrs

# !!! I expect dir to be an input arg for job.run(dir=None), so I should pass
# !!! that through. I need to consider possible overwriting but that may be
# !!! fine based on priority.


class SupervisedJobTask(Task):
    def __init__(
        self,
        # core parts
        job,
        errorhandlers=[],
        dir=None,
        # return, cleanup, and file saving settings
        compress_output=False,
        return_corrections=True,
        save_corrections_tofile=True,
        corrections_filename="simmate_corrections_log.txt",
        # settings for the job supervision
        max_corrections=5,
        polling_timestep=10,
        monitor_freq=30,
        # To support other Prefect input options
        **kwargs,
    ):

        # save input values for reference
        self.job = job
        self.errorhandlers = errorhandlers
        self.dir = dir

        self.max_corrections = max_corrections
        self.polling_timestep = polling_timestep
        self.monitor_freq = monitor_freq

        self.compress_output = compress_output
        self.return_corrections = return_corrections
        self.save_corrections_tofile = save_corrections_tofile
        self.corrections_filename = corrections_filename

        # some errorhandlers run while the job is running. These are known as
        # Monitors and are labled via the is_monitor attribute.
        self.monitors = [h for h in errorhandlers if h.is_monitor]

        # now inherit the parent Prefect Task class
        super().__init__(**kwargs)

    @defaults_from_attrs("job", "dir")
    def run(self, job, dir=None):

        # Establish the working directory for this run.
        # if no directory was provided, use the current working directory
        if not dir:
            dir = os.getcwd()
        # if the user provided a tempdir, we want it's name
        elif isinstance(dir, TemporaryDirectory):
            dir = dir.name
        # otherwise make sure the directory the user provided exists
        else:
            assert os.path.exists(dir)

        # run the initial job setup
        job.setup()

        # We start with zero corrections that we slowly add to. The list only
        # has the columns headers to start.
        # TODO - I took out the headers and may add them back in
        # Headers are... ("applied_errorhandler", "correction_applied")
        corrections = []

        # we can try running the job up to max_corrections. Because only one
        # correction is applied per attempt, you can view this as the maximum
        # number of attempts made on the calculation.
        while len(corrections) < self.max_corrections:

            # launch the job
            # !!! Am I able to do this in an asyncio mode? Because this is a
            # prefect task that is launched through an Executor, it is likely
            # this is running on a single thread worker -- so I'm not sure
            # that asyncio will work here... If I am able to do that, I should
            # move this launch to a Job class method (job.run_aysnc)
            future = job.execute()
            # check that the future is a from subprocess.Popen subprocess
            # Popen returns a __ instead of waiting like subprocess.run()
            is_popen = isinstance(future, Popen)

            # Assume the job has no errors until proven otherwise
            has_error = False

            # Go through the errorhandlers to check for errors until the future
            # completes
            # Only does this if future is an instance of subprocess.Popen
            # !!! elif it is a Dask future or Conncurrent future # TO-DO
            # !!! I would want to run this in async mode so I know exactly when
            # !!! the future completes though.
            # if there aren't any monitors, just wait for the subprocess
            # otherwise loop through the monitors until the job completes
            if self.monitors and is_popen:
                # We want to loop until we find an error and keep track of
                # which loops to run the monitor function on because we don't
                # want them to run nonstop. This variable allows us to
                # every Nth loop.
                monitor_freq_n = 0
                while not has_error:
                    monitor_freq_n += 1
                    # Sleep the set amount before checking the job status
                    time.sleep(self.polling_timestep)

                    # check if the jobs is complete. poll will return 0
                    # when it's done, in which case we break the loop
                    if has_error or future.poll() is not None:
                        break

                    # check whether we should run monitors on this poll loop
                    if monitor_freq_n % self.monitor_freq == 0:
                        # iterate through each monitor
                        for errorhandler in self.monitors:
                            # check if there's an error with this errorhandler
                            # and grab the error if so
                            error = errorhandler.check()
                            if error:

                                # determine if it is_terminating
                                if errorhandler.is_terminating:
                                    # kill the process but don't apply the fix
                                    # quite yet. See below for more on this.
                                    future.terminate()
                                # Otherwise apply the fix and let the job end
                                # naturally. An example of this is for codes
                                # where you add a STOP file to get it to
                                # finish rather than just killing the process.
                                # This is the special case errorhandler that I talk
                                # about in my notes, where we really want to
                                # end the job right away.
                                else:
                                    # apply the fix now
                                    correction = errorhandler.correct()
                                    # record what's been changed
                                    corrections.append(
                                        (errorhandler.name, error, correction)
                                    )

                                # there's no need to look at the other monitors
                                # so break from the for-loop. We also don't
                                # need to monitor the job anymore since we just
                                # terminated it or signaled for its graceful
                                # end. So update the while-loop condition.
                                has_error = True
                                break

            # TO-DO: elif future from dask
            if is_popen:
                # Now just wait for the process to finish
                future.wait()
                # check if the return code is non-zero and
                if future.returncode != 0 and self.terminate_on_nonzero_returncode:
                    raise Exception  # !!! switch to a raising a custom error

            # Check for errors again, because a non-monitor may be higher
            # priority than the monitor triggered about (if there was one).
            # Since the errorhandlers are in order of priority, only the first
            # will actually be applied and then we can retry the calc.
            for errorhandler in self.errorhandlers:

                # NOTE - The following special case is handled above:
                #   errorhandler.is_monitor and not errorhandler.is_terminating
                # I can see this being a source of bugs in the future so I
                # need to reconsider subclassing this special case.

                # check if there's an error with this errorhandler and grab the
                # error if there is one
                error = errorhandler.check()
                if error:
                    # record that the error in case it wasn't done so above
                    has_error = True
                    # And apply the proper correction if there is one.
                    # Some errorhandlers will even raise an error here signaling
                    # that the job is unrecoverable and a lost cause.
                    correction = errorhandler.correct()
                    # record what's been changed
                    corrections.append((errorhandler.name, error, correction))
                    # break from the errorhandler for-loop as we only apply the
                    # highest priority fix and nothing else.
                    break

            # now that we've gone through the errorhandlers, let's see if any
            # non-terminating errors were found (terminating ones would raise
            # an error above). If there are no errors, we've finished the
            # calculation and can exit the while loop. Otherwise, just leave
            # everything where it's at and restart the while-loop with a new
            # attempt
            if not has_error:
                # break the while-loop
                break

        # make sure the while loop didn't exit because of the correction limit
        if len(corrections) >= self.max_corrections:
            raise Exception  # TODO make this a custom exception

        # run the postprocess, which should return the result
        result = job.postprocess()

        # write the log of corrections to file if requested
        if self.save_corrections_tofile:
            with open(self.corrections_filename, "w") as logfile:
                for correction in corrections:
                    logfile.write(f"{correction}\n")

        # compress the output directory for storage if requested
        if self.compress_output:
            make_archive(
                # full path to where to save the archive
                # !!! By default I choose within the current directory and save
                # !!! it as the same name of the directory. This will be a
                # !!! overwritten if I run another job right after it.
                # !!! Consider using a unique filename for each save and returning
                # !!! it, or just using a generic simmate_checkpoint name.
                base_name=os.path.join(os.path.abspath(dir), os.path.basename(dir)),
                # format to use switch to gztar after testing
                format="zip",
                # full path to up tp dir that will be archived
                root_dir=os.path.dirname(dir),
                # directory within root_dir to archive
                base_dir=os.path.basename(dir),
            )

        # Based on the input settings, return either the (result, log) or
        # just the result on its own.
        if self.return_corrections:
            return result, corrections
        else:
            return result