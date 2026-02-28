import React, { useState, useEffect } from 'react'
import { studentAPI } from '../../api/client'

export default function StudentAssignments() {
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    studentAPI.getAssignments()
      .then((res) => {
        setAssignments(res.data.assignments || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">My Assignments</h1>
      
      {loading ? (
        <p>Loading...</p>
      ) : assignments.length > 0 ? (
        <div className="space-y-4">
          {assignments.map((assignment) => (
            <div key={assignment.id} className="card">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{assignment.assignment_id}</h3>
                  <p className="text-gray-600">Status: {assignment.status}</p>
                  {assignment.marks_obtained && (
                    <p className="text-green-600 font-semibold">Marks: {assignment.marks_obtained}</p>
                  )}
                </div>
                {assignment.status === 'pending' && (
                  <button className="btn-primary">Submit</button>
                )}
              </div>
              {assignment.feedback && (
                <p className="mt-2 text-gray-700">Feedback: {assignment.feedback}</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No assignments</p>
      )}
    </div>
  )
}
